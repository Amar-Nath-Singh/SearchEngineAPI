from pydantic import BaseModel


persist_directory="./chroma_db"
embedding_model = "all-MiniLM-L6-v2"
reranker_length = 100
cross_encoder_model = 'cross-encoder/ms-marco-MiniLM-L-6-v2'

API_KEYs = []

allow_origins = ["*"]
allow_credentials = True,
allow_methods=["*"]
allow_headers=["*"]

class SearchQuery(BaseModel):
    query: str
    reranker: bool
    llm: bool
    top_K: int

class EmbededData(BaseModel):
    texts: list[str]
    metadatas: list[dict]
    ids: list[str]
    summarize: bool