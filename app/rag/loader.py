from langchain_community.document_loaders import PyPDFLoader
from typing import List

def load_pdf(file_path: str) -> List[str]:
    loader = PyPDFLoader(file_path)

    documents = loader.load() # returns a list of loaded documents

    print(documents)

    return documents