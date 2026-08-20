from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from app.config.settings import settings
from app.llm.llm_factory import create_llm_provider
from app.pipelines.rag_pipeline import RagPipeline
from app.rag.prompt_builder import PromptBuilder
from app.rag.retriever import Retriever
from app.vectorstore.vector_store import VectorStore


app = FastAPI(
    title="Personal AI Assistant API",
    version="1.0.0"
)


class AskRequest(BaseModel):
    question: str


vector_store = VectorStore()
retriever = Retriever(vector_store)

prompt_path = Path("prompts/rag_system_prompt.txt")
system_prompt = prompt_path.read_text(encoding="utf-8")
prompt_builder = PromptBuilder(system_prompt=system_prompt)

llm = create_llm_provider()

pipeline = RagPipeline(
    retriever=retriever,
    prompt_builder=prompt_builder,
    llm=llm
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/ask")
def ask(request: AskRequest):
    answer = pipeline.ask(request.question)
    return {"answer": answer}
