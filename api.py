from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.config.settings import settings
from app.llm.llm_factory import create_llm_provider
from app.memory.conversation_store import ConversationStore
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
memory_store = ConversationStore(max_messages=10)

prompt_path = Path("prompts/rag_system_prompt.txt")
system_prompt = prompt_path.read_text(encoding="utf-8")
prompt_builder = PromptBuilder(system_prompt=system_prompt)

llm = create_llm_provider()

pipeline = RagPipeline(
    retriever=retriever,
    prompt_builder=prompt_builder,
    llm=llm,
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/ask")
def ask(request: AskRequest):
    memory = memory_store.get(
        user_id=request.user_id,
        conversation_id=request.conversation_id,
    )

    answer = pipeline.ask(
        question=request.question,
        memory=memory,
    )

    return {"answer": answer}
