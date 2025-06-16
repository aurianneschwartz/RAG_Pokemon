import logging
import time

from langchain_google_genai import ChatGoogleGenerativeAI
from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import FactualCorrectness, Faithfulness, LLMContextRecall

from .app import get_and_filter_docs, init_rag_chain

logger = logging.getLogger(__name__)


def eval():
    """Runs the evaluation on the RAG application.
    This function initializes the RAG chain, retrieves relevant documents for sample queries,
    generates responses, and evaluates them against expected responses.
    """
    logger.info("Starting evaluation...")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.1,
        max_output_tokens=3000,
        model_kwargs={"topP": 0.8, "topK": 60},
    )

    sample_queries = [
        "qui est pickachu?",
        "Quel est le type de sulfura ?",
        "qui sont les Oiseaux Légendaires de Kanto?",
        "Quel est le Pokémon le plus célèbre ?",
        "Quels sont les Pokémons de type spectre ?",
        "quel pokemon a le plus d'evolution ?",
        "quel est la particularité de Métamorph?",
        "quel est le nom japonais de Ronflex ?",
    ]
    expected_responses = [
        "Pikachu est un Pokémon de type Électrik, ressemblant à une souris, apparu dès la première génération. C'est le plus célèbre des Pokémon et la mascotte officielle de la licence, notamment en tant que partenaire de Sacha dans le dessin animé. Il est l'évolution de Pichu et peut évoluer en Raichu grâce à une Pierre Foudre."
        "Sulfura est de type Feu et Vol.",
        "Pikachu est le Pokémon le plus célèbre.",
        "Les oiseaux légendaires de kanto sont Artikodin, Électhor et Sulfura.",
        "les Pokémons de type spectre sont: Spectrum, Ectoplasma, Fantominus",
        "D'après le contexte, Évoli est le Pokémon avec le plus d'évolutions possibles, avec un total de 8.",
        "La particularité de Métamorph est sa capacité à se transformer en n'importe quel objet ou créature.",
        "Le nom japonais de Ronflex est カビゴン Kabigon.",
    ]

    dataset = []

    rag_chain = init_rag_chain()

    for query, reference in zip(
        sample_queries[:2],
        expected_responses[:2],
        strict=False,
    ):
        relevant_docs = get_and_filter_docs(query)
        response = rag_chain.invoke(query)["answer"]
        dataset.append(
            {
                "user_input": query,
                "retrieved_contexts": [doc.page_content for doc in relevant_docs],
                "response": response,
                "reference": reference,
            },
        )
        time.sleep(20)
    evaluation_dataset = EvaluationDataset.from_list(dataset)
    evaluator_llm = LangchainLLMWrapper(llm)
    result1 = evaluate(
        dataset=evaluation_dataset,
        metrics=[LLMContextRecall()], # Evaluates how well the LLM recalls the context provided
        llm=evaluator_llm,
    )
    time.sleep(20)
    result2 = evaluate(
        dataset=evaluation_dataset,
        metrics=[Faithfulness()], # Evaluates how faithful the LLM's response is to the provided context
        llm=evaluator_llm,
    )
    time.sleep(20)
    result3 = evaluate(
        dataset=evaluation_dataset,
        metrics=[FactualCorrectness()], # Evaluates the factual correctness of the LLM's responses
        llm=evaluator_llm,
    )
    print(result1, result2, result3)
