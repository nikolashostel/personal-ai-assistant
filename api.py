from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from app.config.settings import settings
from app.llm.gigachat_llm import GigaChatLLM
from app.llm.qwen_llm import QwenLLM
from app.pipelines.rag_pipeline import RagPipeline
from app.rag.prompt_builder import PromptBuilder
from app.rag.retriever import Retriever
from app.vectorstore.vector_store import VectorStore


app = FastAPI(
    title="Enterprise AI Knowledge Assistant API",
    version="1.0.0"
)


class AskRequest(BaseModel):
    question: str


vector_store = VectorStore()
retriever = Retriever(vector_store)

prompt_path = Path("prompts/rag_system_prompt.txt")
system_prompt = prompt_path.read_text(encoding="utf-8")
prompt_builder = PromptBuilder(system_prompt=system_prompt)

if settings.LLM_PROVIDER == "qwen":
    llm = QwenLLM()
else:
    llm = GigaChatLLM()

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
