import os
import json
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from uuid import uuid4
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

def load_rag_file(root_path):
    if 'rag.json' not in os.listdir(os.path.join(root_path, '.mindflow')):
        print("Creating the rag.json file...")
        rag_cache = {'root': root_path, 'file': []}
        with open(os.path.join(root_path, '.mindflow', 'rag.json'), 'w') as f:
            f.write(json.dumps(rag_cache))
    else:
        with open(os.path.join(root_path, '.mindflow', 'rag.json'), 'r') as f:
            rag_cache = json.load(f)
    
    return rag_cache

def update_rag_file(rag_cache, rag_data):
    rag_cache['file'].extend(rag_data)
    with open(os.path.join(rag_cache['root'], '.mindflow', 'rag.json'), 'w') as f:
        f.write(json.dumps(rag_cache))
        
    return rag_cache
            

def list_md_files(directory, cache=[]):
    """
    List all the Markdown files in the provided directory and its subdirectories.
    
    :param directory: The directory to search for Markdown files.
    :return: A list of dictionaries containing the absolute and relative paths of the Markdown files.
    """
    md_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md') and (os.path.relpath(os.path.join(root, file), directory) not in cache):
                md_files.append({
                    "absolute_path": os.path.join(root, file),
                    "relative_path": os.path.relpath(os.path.join(root, file), directory)
                })
    return md_files

def init_vector_store(embeddings, root_path, index_name="notes_index"):
    index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    vector_store.save_local(os.path.join(root_path, '.mindflow', index_name))
    
    return vector_store


def embed_documents(vector_store, md_files, rag_cache, root_path, index="notes_index"):
    if len(md_files) == 0:
        return vector_store, rag_cache
    documents = []
    rag_cache = update_rag_file(rag_cache, [file['relative_path'] for file in md_files])
    for file in md_files:
        with open(file["absolute_path"], 'r') as f:
            content = f.read()
        contents = text_splitter.split_text(content)
        for content in contents:
            doc = Document(page_content=content, metadata={"source": file["relative_path"]})
            documents.append(doc)
    
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=uuids)
    vector_store.save_local(os.path.join(root_path, '.mindflow', index))
    
    return vector_store, rag_cache


def load_vector_store(embeddings, root_path, index_name="notes_index"):
    if index_name not in os.listdir(os.path.join(root_path, '.mindflow')):
        return init_vector_store(embeddings, root_path, index_name)
    
    vector_store = FAISS.load_local(
        os.path.join(root_path, '.mindflow', index_name), embeddings, allow_dangerous_deserialization=True
    )
    return vector_store


def search_documents(vector_store: FAISS, query: str, target=None, k=3):
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})
    if target is not None:
        return retriever.invoke(query, filter={"source": target})
    return retriever.invoke(query)


if __name__ == "__main__":
    root_path = "/Users/USER/Desktop/Side_project/MindFlow-AI/note_part/data/TestingNote"
    rag_cache = load_rag_file(root_path)
    md_files = list_md_files(root_path, rag_cache['file'])
    vector_store = load_vector_store(embeddings, root_path)
    
    vector_store, rag_cache = embed_documents(vector_store, md_files, rag_cache, root_path)
    # results = search_documents(vector_store, "What is multi-agent system?", target=['paper/Large Language Model based Multi-Agents- A Survey of Progress and Challenges.md', 'paper/Massive Text Embedding Benchmark.md'])
    # for result in results:
    #     print(result.metadata)
    #     print(result.page_content)
    #     print("-" * 100)