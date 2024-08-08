from sentence_transformers import CrossEncoder
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

from config import *

app = FastAPI()
security = HTTPBearer()

embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
vectorstore = Chroma(embedding_function=embeddings, persist_directory = persist_directory)
reranker = CrossEncoder(cross_encoder_model, max_length=reranker_length)

# Add CORS middleware
app.add_middleware(
CORSMiddleware,
allow_origins = allow_origins,  # Allows all origins
allow_credentials = allow_credentials,
allow_methods = allow_methods,  # Allows all methods
allow_headers = allow_headers,  # Allows all headers
)

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials.credentials in API_KEYs:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )
    
@app.post('/embeded_data/')
async def embeded_data(data: EmbededData, credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    vectorstore.add_texts(texts=data.texts, metadatas = data.metadatas, ids=data.ids)


@app.post('/search/')
async def search(search_query: SearchQuery,  credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    query = search_query.query
    k = search_query.top_K
    if not k > 0:
        return [ {'metadata' : None, "page_content": None, "retriever_score" : None, "reranker_score" : None}]
    
    results = vectorstore.similarity_search_with_score(query=query, k=k)
    if search_query.reranker:
        reranker_scores = reranker.predict([(query, result.page_content) for result, score in results])
        reranked_results = sorted(zip(results, reranker_scores), key = lambda pari: pari[1], reverse = True)
        out_schema = [ {'metadata' : result.metadata, "page_content": result.page_content, "retriever_score" : str(score), "reranker_score" : str(rr_score)} for (result, score), rr_score in reranked_results]
    else:
        out_schema = [ {'metadata' : result.metadata, "page_content": result.page_content, "retriever_score" : str(score), "reranker_score" : str(0.0)} for (result, score) in results]

    return out_schema




 