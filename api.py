from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.config.settings import settings
from app.db.database import SessionLocal
from app.db.init_db import init_db
from app.db.repositories import ConversationRepository
from app.llm.llm_factory import create_llm_provider
from app.memory.conversation_memory import ConversationMemory
from app.pipelines.rag_pipeline import RagPipeline
from app.rag.prompt_builder import PromptBuilder
from app.rag.retriever import Retriever
from app.vectorstore.vector_store import VectorStore


app = FastAPI(
    title="Personal AI Assistant API",
    version="1.0.0"
)


class AskRequest(BaseModel):
    user_id: str = Field(min_length=1)
    conversation_id: str = Field(min_length=1)
    question: str = Field(min_length=1)


vector_store = VectorStore()
retriever = Retriever(vector_store)

prompt_path = Path("prompts/rag_system_prompt.txt")
system_prompt = prompt_path.read_text(encoding="utf-8")
prompt_builder = PromptBuilder(system_prompt=system_prompt)

llm = create_llm_provider()

pipeline = RagPipeline(
    retriever=retriever,
    prompt_builder=prompt_builder,
    llm=llm,
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/ask")
def ask(request: AskRequest):
    db = SessionLocal()

    try:
        repository = ConversationRepository(db)
        user = repository.get_or_create_user(request.user_id)
        conversation = repository.get_or_create_conversation(
            user=user,
            external_id=request.conversation_id,
        )

        memory = ConversationMemory(max_messages=10)
        for message in repository.get_recent_messages(conversation, limit=10):
            if message.role == "user":
                memory.add_user_message(message.content)
            elif message.role == "assistant":
                memory.add_assistant_message(message.content)

        answer = pipeline.ask(
            question=request.question,
            memory=memory,
        )

        repository.add_message(
            conversation=conversation,
            role="user",
            content=request.question,
        )
        repository.add_message(
            conversation=conversation,
            role="assistant",
            content=answer,
        )

        db.commit()

        return {"answer": answer}

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
