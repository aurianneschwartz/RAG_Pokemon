import argparse
import logging
import os
import subprocess
import sys

from .app import app
from .create_vectorstore import create_vectorstore
from .download_dataset import download_dataset
from .eval import eval

DATASET_FOLDER = "pokemon_dataset"
VECTORSTORE_FILE = "chroma_db"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def ensure_dataset():
    """
    Ensures the dataset folder exist and is not empty. If not, it prompts the user to download
    the default dataset and handles the consequences.
    """
    if not (os.path.exists(DATASET_FOLDER) and os.listdir(DATASET_FOLDER)):
        response = (
            input(
                f"There is no '{DATASET_FOLDER}' folder or it's empty. Would you like to download the default one? [Y/n]: ",
            )
            .strip()
            .lower()
        )
        if response in ("y", ""):
            logger.info("Downloading default dataset...")
            download_dataset()
        else:
            logger.error(
                "Error: Please execute first 'python -m RAG --download-dataset [the pokemon gen you want]' to get a dataset.",
            )
            sys.exit(1)


if __name__ == "__main__":
    """
    Parses command-line arguments and calls the appropriate functions.
    """
    parser = argparse.ArgumentParser(
        prog="RAG",
        description="A package for RAG (Retrieval-Augmented Generation) operations.",
        formatter_class=argparse.RawTextHelpFormatter,  # For better help formatting
    )
    
    parser.add_argument(
        "--download-dataset",
        metavar="DATASET_NAME",
        nargs="?", 
        const=True,
        help="Download a specific pokemon generation. If no name is provided, the gen 1 will be downloaded.\nExample: python -m RAG --download-dataset 1",
    )
    parser.add_argument(
        "--create-vectorstore",
        action="store_true",
        help="Create the vector store from the available dataset.",
    )
    parser.add_argument(
        "--app",
        action="store_true",
        help="Launch the RAG application.",
    )
    parser.add_argument(
        "--eval",
        action="store_true",
        help="Run the evaluation on the RAG application.",
    )
    parser.add_argument(
        "--app_streamlit",
        action="store_true",
        help="Launch the RAG application on Streamlit.",
    )

    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        response = (
            input(
                "No command provided. Would you like to launch the RAG application? [Y/n]: ",
            )
            .strip()
            .lower()
        )
        if response in ("y", ""):
            logger.info("Defaulting to --app based on user confirmation.")
            args.app = True  # Proceed to run the app
        else:
            logger.info("No action selected. Exiting gracefully.")
            sys.exit(0)  # Exit cleanly if user declines or gives invalid input

    if args.download_dataset is not None:
        if args.download_dataset is True: 
            download_dataset()  
        else:
            download_dataset(args.download_dataset)  
    elif args.create_vectorstore:
        # Ensure dataset is ready before creating vector store
        ensure_dataset()
        create_vectorstore()
    elif args.app:
        # Check if vector store exists before launching app
        if not os.path.exists(VECTORSTORE_FILE):
            logger.info(
                f"There is no vector store at '{VECTORSTORE_FILE}'.\nAttempting to create the vector store...",
            )
            ensure_dataset()
            create_vectorstore()
        app()
    elif args.eval:
        if not os.path.exists(VECTORSTORE_FILE):
            logger.info(
                f"There is no vector store at '{VECTORSTORE_FILE}'.\nAttempting to create the vector store...",
            )
            ensure_dataset()
            create_vectorstore()
        eval()
    elif args.app_streamlit:
        subprocess.run(
            ["streamlit", "run", os.path.join("RAG", "app_streamlit.py")], check=False
        )
