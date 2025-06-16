from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, UnstructuredHTMLLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

def create_vectorstore():
    """Creates a vector store from the downloaded HTML files in the 'pokemon_dataset' directory.
    The vector store is created using LangChain's Chroma and GoogleGenerativeAIEmbeddings.
    """
    loader = DirectoryLoader("./pokemon_dataset/", loader_cls=UnstructuredHTMLLoader)
    docs = loader.load()
    # Extract the text from the website data document
    for doc in docs:
        text_content = doc.page_content
        text_content = text_content.replace("[modifier]", "")
        text_content = "№" + text_content.split("№")[1]
        text_content = text_content.split("Dans le Jeu de Cartes à Collectionner")[0]
        doc.page_content = "".join(text_content)
    gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    Chroma.from_documents(
        documents=docs,
        embedding=gemini_embeddings,
        persist_directory="./chroma_db",
    )
