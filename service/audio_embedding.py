from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_community.document_loaders import AssemblyAIAudioTranscriptLoader
from constants import app_constants


transcripts = []


class TranscriptProcessor:
    def __init__(self, chroma_db):
        self.chroma_db = chroma_db
        self.transcripts = []

    def load_transcripts(self, audio_files):
        global transcripts
        self.transcripts = []
        for audio_file in audio_files:
            try:
                transcript_loader = AssemblyAIAudioTranscriptLoader(
                    file_path=audio_file)
                docs = transcript_loader.load()

                # Filter complex metadata
                docs = filter_complex_metadata(docs)

                texts = RecursiveCharacterTextSplitter(
                    chunk_size=app_constants.CHUNK_SIZE, chunk_overlap=app_constants.CHUNK_OVERLAP).split_documents(docs)

                for text_segment in texts:
                    self.chroma_db.add_documents([text_segment])
                self.chroma_db.persist()

                for text_segment in texts:
                    self.transcripts.append(text_segment.page_content.strip())
                print(
                    f"Processed and added transcript for audio file: {audio_file}")

            except Exception as e:
                print(f"Error processing audio file {audio_file}: {e}")

        return self.transcripts

    def get_transcripts(self):
        global transcripts
        return transcripts
