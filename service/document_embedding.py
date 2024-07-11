import os
from langchain_community.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, UnstructuredExcelLoader
from langchain.text_splitter import CharacterTextSplitter
from constants import app_constants


class DocumentProcessor:
    def __init__(self, chroma_db):
        self.chroma_db = chroma_db

    def process_documents(self, document_paths):
        for document_path in document_paths:
            # try:
            # Determine the file type based on the file extension
            _, file_extension = os.path.splitext(document_path)
            file_extension = file_extension.lower()

            if file_extension == '.pdf':
                loader = PyPDFLoader(document_path)

            elif file_extension == '.docx':
                loader = UnstructuredWordDocumentLoader(document_path)

            elif file_extension == '.xlsx':
                loader = UnstructuredExcelLoader(document_path)

            else:
                print(f"Unsupported file type: {file_extension}")
                continue

            if file_extension in {'.pdf', '.docx', '.xlsx'}:
                # Load the document
                documents = loader.load()
                print(f"document: {documents}")
                # Split the document into chunks
                text_splitter = CharacterTextSplitter(
                    chunk_size=app_constants.CHUNK_SIZE, chunk_overlap=app_constants.CHUNK_OVERLAP)
                texts = text_splitter.split_documents(documents)
                print(f"text: {texts}")
                # Add new documents to the Chroma DB
                self.chroma_db.add_documents(texts)
                self.chroma_db.persist()
                print(f"Processed and added document: {document_path}")
            # except Exception as e:
            #     print(f"Error processing document {document_path}: {e}")
        print("-----------")
