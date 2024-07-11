import cv2
import pytesseract
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema.document import Document
from constants import app_constants


class ImageProcessor:
    def __init__(self, chroma_db):
        self.chroma_db = chroma_db

    def add_images(self, image_paths):

        for image_path in image_paths:
            try:

                # Read the image using OpenCV
                img = cv2.imread(image_path)

                # Extract text from the image using pytesseract
                text = pytesseract.image_to_string(img)

                text_splitter = CharacterTextSplitter(
                    chunk_size=app_constants.CHUNK_SIZE, chunk_overlap=app_constants.CHUNK_OVERLAP)
                texts = [Document(page_content=x)
                         for x in text_splitter.split_text(text)]
                # Add new documents to the Chroma DB
                self.chroma_db.add_documents(texts)
                self.chroma_db.persist()

                print(f"Processed and added image: {image_path}")
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
