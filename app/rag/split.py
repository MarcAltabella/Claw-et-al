from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


def splitter(docs: List[str]) -> List[str]:

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # chunk size (characters)
        chunk_overlap=200,  # chunk overlap (characters)
        add_start_index=True,  # track index in original document
    )

    all_splits_list = text_splitter.split_documents(docs) # returns a list of split documents
    print(f"Split blog post into {len(all_splits_list)} sub-documents.")
    
    return all_splits_list