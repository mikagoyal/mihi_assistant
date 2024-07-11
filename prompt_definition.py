from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.prompts import PromptTemplate
import embeddings
from flask_socketio import emit
import time
from constants import app_constants

# Initialise global variables
conversation_retrieval_chain = None
chat_history = []


class Streaming(BaseCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        emit('stream_response', {'data': token})
        time.sleep(app_constants.TIME)


template = """You are a friendly AI assistant and your name is `Mihi Assistant`. Your responsibility is to answer questions based on documents knowledge base. If you did not find the answer from the documents say 'I'm sorry I'm not able to find a relevant answer as per your question'.
If the user asks you your name, you only respond with: "Hi, I'm Mihi Assistant. How can I assist you today?".
Always respond with short but complete answers unless the user specifically asks to elaborate on something.
If the user says "tell me more about this" or something similar, look at the chat history and refer to the provided documents to give more details about the previously asked question.
Here is a question about the document: {input}
Answer:
"""

prompt = PromptTemplate(input_variables=['input'], template=template)

# Add conversational memory
memory = ConversationBufferMemory(
    memory_key='chat_history', return_messages=True, output_key='text')
# Create a retriever interface from the vector store
retriever = embeddings.chroma_db.as_retriever(
    search_type="similarity", search_kwargs={"k": app_constants.K})

# Create a conversational retrieval chain from the language model and the retriever
conversation_retrieval_chain = ConversationalRetrievalChain.from_llm(llm=embeddings.llm,
                                                                     retriever=retriever,
                                                                     memory=memory,
                                                                     callbacks=[
                                                                         Streaming()]
                                                                     )

chain = LLMChain(llm=embeddings.llm, prompt=prompt,
                 memory=memory, callbacks=[Streaming()])


def get_answer_from_chain(question):
    # result = conversation_retrieval_chain({"question": question})
    # return result["answer"]
    global chat_history
    context_str = " ".join(
        map(lambda x: f"User: {x[0]} Bot: {x[1]}", chat_history)) + " User: " + question
    retriever = embeddings.chroma_db.as_retriever(
        search_type="similarity", search_kwargs={"k": app_constants.K})
    docs = retriever.get_relevant_documents(question)
    context_str += " " + " ".join([str(doc) for doc in docs])
    result = chain.run(input=context_str)
    chat_history.append((question, result))
    return result
