from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os

load_dotenv()
def store():
    path = "/app/MeisterCompetencyCertificationCriteriabyArea_2024.pdf"
    loadder = PyPDFLoader(file_path=path)
    documment = loadder.load()
    spliter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100, separator="\n")
    text = spliter.split_documents(documment)
    embedder = OpenAIEmbeddings()
    PineconeVectorStore.from_documents(documents=text, embedding=embedder, index_name=os.getenv("PINECONE_PDF_INDEX"))

if __name__ == "__main__":
    store()