import re
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser
from langchain_community.document_loaders import YoutubeAudioLoader


class VideoProcessor:
    def __init__(self, chroma_db):
        self.chroma_db = chroma_db

    def load_videos(self, user_prompt):
        try:
            video_link = re.search(r'https?://\S+', user_prompt).group()
            save_dir = "uploads"
            loader = GenericLoader(YoutubeAudioLoader([video_link], save_dir),
                                   OpenAIWhisperParser()
                                   )
            docs = loader.load()

            for doc in docs:
                self.chroma_db.add_documents([doc])
            self.chroma_db.persist()

            print("Video embedded successfully")
        except Exception as e:
            print(f"Error embedding video: {e}")
