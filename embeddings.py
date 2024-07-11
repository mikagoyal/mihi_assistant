import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from service import audio_embedding, document_embedding, generate_image, image_embedding, video_embedding

OPENAI_API_KEY = "sk-proj-..."
# Load environment variables
load_dotenv()

# Initialise global variables
llm = None
llm_embeddings = None
chroma_db = None

# Function to initialise Chroma DB from existing documents


def init_chroma_db():
    global chroma_db
    # Check if Chroma DB already exists
    persist_directory = "./data"
    if os.path.exists(persist_directory):
        # Load existing Chroma DB
        chroma_db = Chroma(persist_directory=persist_directory,
                           embedding_function=llm_embeddings)
    else:
        # Create a new Chroma DB if it does not exist
        chroma_db = Chroma(embedding_function=llm_embeddings)

# Function to initialise the language model and its embeddings


def init_llm():
    global llm, llm_embeddings
    # Initialise the language model with the OpenAI API key
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(streaming=True, model_name="gpt-4",
                     openai_api_key=OPENAI_API_KEY)
    # Initialise the embeddings for the language model
    llm_embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)


init_llm()
init_chroma_db()

audio = audio_embedding.TranscriptProcessor(chroma_db)
video = video_embedding.VideoProcessor(chroma_db)
doc = document_embedding.DocumentProcessor(chroma_db)
image = image_embedding.ImageProcessor(chroma_db)
generate_img = generate_image.ImageGenerator(OPENAI_API_KEY)
