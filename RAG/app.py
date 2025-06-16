from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.schema import StrOutputParser
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache


set_llm_cache(InMemoryCache())

load_dotenv()

RELEVANCE_THRESHOLD = 0.55

def get_and_filter_docs(query: str) -> list[Document]:
    """Retrieve the documents and filter them directly based on their relevance score."""
    gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=gemini_embeddings,
    )
    docs_with_scores = vectorstore.similarity_search_with_relevance_scores(query, k=10)
    return [doc for doc, score in docs_with_scores if score >= RELEVANCE_THRESHOLD]


def format_docs(docs: list[Document]) -> str:
    """Format the documents for the LLM input."""
    return "\n\n".join(doc.page_content for doc in docs)


def init_rag_chain() -> RunnableParallel:
    """Initialize the RAG chain with LangChain."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.1, #low temperature for more deterministic responses
        max_output_tokens=3000, # high max output tokens to allow for detailed responses
        model_kwargs={"topP": 0.8, "topK": 60}, # topP and topK for better quality responses
    )
    llm_prompt = PromptTemplate.from_template(
        """
    Tu es un assistant spécialiste de l'univers Pokémon.
    Tu réponds en peu de phrases, de manière claire, concise et directe.

    - Utilise UNIQUEMENT le contexte fourni pour répondre.
    - Si la question demande une donnée précise, donne une réponse brève et exacte.
    - Si la question est plus large, essaie de tirer une réponse utile du contexte et développe un peu plus la réponse (quelques phrases).
    - Si c’est subjectif, tu peux ajouter une touche d’humour, mais toujours avec une réponse.
    - Si le contexte ne permet pas de répondre, dis simplement : "Je ne sais pas."

    Question : {question}
    Contexte : {context}

    Réponse :
    """,
    )
    retriever_with_filter = RunnableLambda(get_and_filter_docs)
    setup_and_retrieval = RunnableParallel(
        {"context": retriever_with_filter, "question": RunnablePassthrough()},
    )

    answer_generation_chain = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | llm_prompt
        | llm
        | StrOutputParser()
    )
    return setup_and_retrieval.assign(
        answer=answer_generation_chain,
    )


def app():
    """Initialize the RAG application with LangChain."""
    rag_chain = init_rag_chain()
    while True:
        requete = input("Posez votre question sur l'univers Pokémon : ")
        print(rag_chain.invoke(requete)["answer"])


def get_answer(query: str) -> str:
    """Retrieve an answer from the RAG system based on the input query."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.1, #low temperature for more deterministic responses
        max_output_tokens=3000, # high max output tokens to allow for detailed responses
        model_kwargs={"topP": 0.8, "topK": 60}, # topP and topK for better quality responses
    )
    llm_prompt = PromptTemplate.from_template(
        """
        Tu es un assistant spécialiste de l'univers Pokémon.
        Tu réponds en peu de phrases, de manière claire, concise et directe.

        - Utilise UNIQUEMENT le contexte fourni pour répondre.
        - Si la question demande une donnée précise, donne une réponse brève et exacte.
        - Si la question est plus large, essaie de tirer une réponse utile du contexte et développe un peu plus la réponse (quelques phrases).
        - Si c’est subjectif, tu peux ajouter une touche d’humour, mais toujours avec une réponse.
        - Si le contexte ne permet pas de répondre, dis simplement : "Je ne sais pas."

        Question : {question}
        Contexte : {context}

        Réponse :
        """,
    )
    retriever_with_filter = RunnableLambda(get_and_filter_docs)
    setup_and_retrieval = RunnableParallel(
        {"context": retriever_with_filter, "question": RunnablePassthrough()},
    )
    answer_generation_chain = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | llm_prompt
        | llm
        | StrOutputParser()
    )
    rag_chain = setup_and_retrieval.assign(
        answer=answer_generation_chain,
    )
    return rag_chain.invoke(query)["answer"]
