# ruff: noqa: E402
"""
Document ingestion script for RAG implementation.
Load documents (txt, json, csv) from data/documents folder, splits them into chunks,
and store them in a Chroma vector database (persistent local).
Ref: https://github.com/promptfoo/promptfoo/tree/main/examples/rag-full

Usage: `make ingest_documents`
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import List, Tuple

from dotenv import find_dotenv, load_dotenv
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from tqdm import tqdm

# Load the .env file
load_dotenv(find_dotenv(), override=True)

# CONFIG PATH WHEN RUN SCRIPT TO ALLOW IMPORT MODULE FROM PARENT DIR: server
# ----------------------------------------------------------------
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
# from remote_pdb import RemotePdb
# RemotePdb('127.0.0.1', 4444).set_trace()
if root_path not in sys.path:
    sys.path.append(root_path)
import agent.llms as llms
import utils.constants as constants

# ----------------------------------------------------------------
# After allow import module from parent dir: server
import utils.utils as utils
from agent.rag.loader import BaseLoader  # noqa: E402

# ------------------ Allow parse args ------------------
# Create a parser object
parser = argparse.ArgumentParser()
# Add an argument
parser.add_argument("--force", type=str, help="Force recreate the database")
# Parse the arguments
parser_args = parser.parse_args()
# ------------------ End allow parse args ------------------

ROOT_PATH = "server"
VECTOR_STORE_PATH = f"{ROOT_PATH}/{constants.VECTOR_STORE_PATH}"
BASE_DOCUMENTS_FOLDER = f"{ROOT_PATH}/{constants.BASE_DOCUMENTS_FOLDER}"


def process_files(files) -> List[Document]:
    """
    Process files and split them into chunks

    Returns:
        List of document chunks
    """

    def process_single_file(
        file_name: str, metadata=None
    ) -> Tuple[str, List[Document]]:
        """
        Process a single text file and return it chunks

        Args:
            file_name (str): Name of the text file to process

        Returns:
            Tuple containing filename and list of document chunks
        """
        try:
            print(
                "Processing :",
                utils.get_path(file_name, BASE_DOCUMENTS_FOLDER),
            )
            documents = BaseLoader.load_file(
                utils.get_path(file_name, BASE_DOCUMENTS_FOLDER), metadata=metadata
            )
            text_splitter: RecursiveCharacterTextSplitter = (
                RecursiveCharacterTextSplitter(
                    chunk_size=constants.SPLITTER_TEXT_CHUNK_SIZE,
                    chunk_overlap=constants.SPLITTER_TEXT_CHUNK_OVERLAP,
                )
            )
            chunks: List[Document] = text_splitter.split_documents(documents)
            return file_name, chunks
        except Exception as e:
            logging.error(f"Error processing {file_name}: {str(e)}")
            return file_name, []

    all_chunks: List[Document] = []
    print("START PROCESS FILES:", files)

    for text_file in files:
        file_name = text_file["file_name"]
        metadata = text_file["metadata"]
        _, chunks = process_single_file(file_name, metadata)
        all_chunks.extend(chunks)
        logging.info(f"Processed {len(all_chunks)} text file chunks")

    return all_chunks


def create_vector_store(chunks: List[Document], batch_size: int = 10) -> None:
    """
    Create and persist the vector store from document chunks in batches.

    Args:
        chunks: List of document chunks to embed
        batch_size: Number of documents to process in each batch
    """
    logging.info("Creating main vector store ...")

    # Process first batch
    current_batch: List[Document] = chunks[:batch_size]
    db: Chroma = Chroma.from_documents(
        current_batch,
        llms.embeddings_model,
        persist_directory=VECTOR_STORE_PATH,
        collection_name=constants.VECTOR_STORE_COLLECTION_NAME,
    )
    with tqdm(
        total=len(chunks), initial=batch_size, desc="Embedding documents"
    ) as pbar:
        for i in range(batch_size, len(chunks), batch_size):
            current_batch = chunks[i : i + batch_size]
            db.add_documents(current_batch)
            pbar.update(batch_size)

    logging.info("Main vector store created successfully.")


def main() -> None:
    """Main execution function."""
    logging.info("Starting document ingestion ...")
    if not parser_args.force and utils.is_chroma_db_exist(VECTOR_STORE_PATH):
        # Not allow to recreate the database if not force
        logging.info(
            "Chroma database already exists. If you want to recreate it, delete the existing one."
        )
        return

    chunks: List[Document] = process_files(
        [
            {
                "file_name": "faqs.txt",
                "metadata": {"source": "faqs.txt", "service_category": "faqs"},
            },
            {
                "file_name": "policies.yaml",
                "metadata": {"source": "policies.yaml", "service_category": "policies"},
            },
        ]
    )
    if chunks:
        # Create vector store persistently in CHROMA_PATH
        create_vector_store(chunks)


if __name__ == "__main__":
    main()
