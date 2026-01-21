from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant.fastembed_sparse import FastEmbedSparse

GEMINI_KEY = "AIzaSyCMMm7skFh74Co58A4awJDk8oVglUlyaFs"

dense_embeddings = GoogleGenerativeAIEmbeddings(
    model="text-embedding-004",
    google_api_key=GEMINI_KEY
)

sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
