import os
import re
import getpass
import langchain
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import CacheBackedEmbeddings
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.storage import LocalFileStore
from typing import List, Union

from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI


os.environ["OPENAI_API_KEY"] = getpass.getpass("Your OpenAI API Key:")

def split_text(document: List) -> List[langchain.schema.document.Document]:
    """Two type of split: 
    - CharacterTextSplitter: split based on characters passed in, \n
    chunk size is amount of characters
    - RecursiveTextSplitter: split based on semantical units (e.g sentences) \n
    chunk size is numberd of characters or tokens -> We use this 
    """
    text_split = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
        length_function=len)
    
    chunks = text_split.transform_documents(document)
    print('Splitting done')
    return chunks

