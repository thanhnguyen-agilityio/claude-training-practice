import os
from typing import Iterator

import yaml
from langchain.schema import Document
from langchain_community.document_loaders import TextLoader


class BaseLoader:
    """Base loader for LangChain RAG, dynamically selects the appropriate loader by file extension."""

    @staticmethod
    def load_file(file_path: str, metadata=None):
        """
        Loads a file using the appropriate loader based on its extension.

        Args:
            file_path (str): Path to the file.
            metadata: Optional metadata to pass to the loader.

        Returns:
            list: A list of documents loaded by LangChain loaders.

        Raises:
            ValueError: If the file extension is unsupported.
        """
        # Ensure file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine the file extension
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        # Select appropriate loader based on file extension
        if file_extension == ".txt":
            return CustomTextLoader(file_path, metadata=metadata).load()
        elif file_extension in (".yaml", ".yml"):
            return YAMLLoader(file_path, metadata=metadata).lazy_load()
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")


class CustomTextLoader(TextLoader):
    def __init__(self, file_path: str, metadata=None):
        super().__init__(file_path)
        self.metadata = metadata

    def load(self):
        # Load the documents using the original load method
        documents = super().load()

        # Apply the metadata function to each document if provided
        if self.metadata:
            for doc in documents:
                # Generate metadata using the provided function
                doc.metadata = self.metadata
            return documents

        return documents


class YAMLLoader(BaseLoader):
    """Custom YAML loader that reads and splits a YAML file into structured Documents."""

    def __init__(self, file_path: str, metadata=None) -> None:
        """
        Initialize the loader with the file path.

        Args:
            file_path (str): The path to the YAML file.
        """
        self.file_path = file_path
        self.metadata = metadata

    def lazy_load(self) -> Iterator[Document]:
        """
        A lazy loader that reads a YAML file and yields documents.

        Yields:
            Document: A LangChain Document object for each YAML structure.
        """
        with open(self.file_path, "r", encoding="utf-8") as file:
            yaml_content = yaml.safe_load(file)

        if isinstance(yaml_content, dict):
            # Yield one Document per top-level key-value pair
            for key, value in yaml_content.items():
                content = yaml.dump({key: value}, default_flow_style=False)
                yield Document(
                    page_content=content,
                    metadata={**self.metadata, "key": key},
                )
        elif isinstance(yaml_content, list):
            # Yield one Document per list item
            for _, item in enumerate(yaml_content):
                content = yaml.dump(item, default_flow_style=False)
                yield Document(
                    page_content=content,
                    metadata={**self.metadata, "key": key},
                )
        else:
            # Handle scalar values as a single document
            content = yaml.dump(yaml_content, default_flow_style=False)
            yield Document(page_content=content, metadata=self.metadata)
