#%%
import os, sys
import re
import getpass
#import PyPDF2
#import pdfminer.high_level as high
import langchain
from langchain.schema.document import Document
from langchain.loaders.pdf_loader import PDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import CacheBackedEmbeddings
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.storage import LocalFileStore
from typing import List, Union
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI

#%%
os.environ["OPENAI_API_KEY"] = getpass.getpass("Your OpenAI API Key:")

#%%


'''def pdf_extraction(pdf_filename):

    pdf_path = os.path.join(os.getcwd(), os.pardir,'data', pdf_filename)
    text = ""

    try:
        # Load the PDF file into a Document object
        document = PDFLoader(pdf_path=pdf_path).load()

        # Get the text content of the Document object
        text = document.page_content

    except Exception as e:
        print(e)

    return text'''


def pdf_extraction(pdf_filenames):
    '''
    Load pdfs as document objects
    Aim: get text contents (metadata) and pages 
    Benefits: data/document transformation, e.g json string as input
    '''
    pdf_path = os.path.join(os.getcwd(), os.pardir,'data')
    documents = []

    try:
        # Loop through the PDF filenames
        for pdf_filename in pdf_filenames:
            # Load each PDF file into a Document object
            document = PDFLoader(pdf_path=os.path.join(pdf_path, pdf_filename)).load()

            # Append the Documewnt object to the list
            documents.append(document)

    except Exception as e:
        print(e)

    return documents


def split_text(documents: List) -> List[langchain.schema.document.Document]:
    """ 
    langchain.schema.document.Document
    - list of document objects, which a document object as dictionary made of 2 keys
    + page_content (values) and metadata (just dictionaries)

    Two types of split: 
    - CharacterTextSplitter: split based on characters passed in, \n
    chunk size is amount of characters
    - RecursiveTextSplitter: split based on semantical units (e.g sentences) \n
    chunk size is numberd of characters or tokens -> We use this 
    """
    print("Splitting process...")
    text_split = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
        length_function=len)
    
    chunks = text_split.transform_documents(documents)
    print('Splitting done')
    return chunks


def doc_embedding(chunks: List, emb_type) -> langchain.embeddings.cache.CacheBackedEmbeddings:
    """
    Construct an Embedder (get embeddings from chunks) with
    - CacheBackedEmbeddings: local cache, interface for caching results
    (embedder and a document embedding store)
    - Some types of embeddings (emb_type): OpenAI, HuggingFace, etc
    """
    print("Constructing Embedder...")
    store = LocalFileStore("./cache/")
    # Choose embedding type
    if emb_type == 'openai':
        emb_model = OpenAIEmbeddings()
    if emb_type == 'huggingface':
        emb_model = HuggingFaceEmbeddings()
    else:
        raise ValueError(f'Unsupported embedding type: {emb_type}')
    
    embedder = CacheBackedEmbeddings(
        emb_model,
        store,
        namespace=emb_model.model
    )
    print('Embedder is ready!')
    return embedder


def vector_store(chunks: List[langchain.schema.document.Document],
                 embedder: langchain.embedding.cache.CacheBackedEmbeddings) -> langchain.vectorstores.faiss.FAISS:
    """
    Using embedder to transform chunks into vectors,
    then using FAISS (similarity search and clustering of dense vectors) to store and query them
    """
    print('Creating vector store...')
    vector_store = FAISS.from_documents(chunks, embedder)
    return vector_store


def vector_retriever(vectorstore: langchain.vectorstores) -> langchain.vectorstores.base.VectorStoreRetriever:
    """
    Aim: Allow querying and retrieval of similar vectors/documents from the vector store.

    Parameters:
    - vectorstore: FAISS vector store with vectors of document chunks.

    Returns:
    - langchain.vectorstores.base.VectorStoreRetriever: A retriever object for querying
      and retrieving similar vectors/documents from the vector store.

    """
    print("Creating vectorstore retriever...")
    retriever = vectorstore.as_retriever()
    return retriever


def embed_user_query(query: str) -> List[float]:
    """
    Input: user query -> transforms it into a vector representation with relevant embeddings models

    Parameters:
    - query (str): The user query to be embedded.

    Returns:
    - List[float]: A list of floats representing the embedded vector of the user query.
    """
    emb_model = OpenAIEmbeddings()
    embedded_query = emb_model.embed_query(query)
    return embedded_query


def similarity_search(vectorstore: langchain.vectorstores,
                      embedded_query: List[float]) -> List[langchain.schema.document.Document]:
    """
    Perform the most similar vectors/documents based on the embedded query.

    Parameters:
    - vectorstore (langchain.vectorstores)
    - embedded_query (List[float]): A list of floats representing the embedded vector of the user query.

    Returns:
    - A list of Document objects most similar to the embedded query (choose k for ranking)
    """
    response = vectorstore.similarity_search_by_vector(embedded_query, k=2)
    return response


def create_chatbot(retriever: langchain.vectorstores) -> langchain.chains.conversational_retrieval:
    '''
    ConversationBufferMemory: store and access the history of a conversation (memory)
    '''
    llm = ChatOpenAI(model="gpt-3.5-turbo")

    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True
        )

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory
        )
    return conversation_chain


def chat(conversation_chain, input: str) -> str:
    """
    Take a user input (str), passes it to the chatbot for processing,
    and retrieves the chatbot's response (str)
    """
    return conversation_chain.run(input)