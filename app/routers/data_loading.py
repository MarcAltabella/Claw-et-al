import os

from uuid import uuid4
from fastapi import HTTPException, status, Depends, APIRouter, UploadFile, File
from sqlalchemy.orm import Session
from ..oauth2 import get_current_user
from ..rag import pipeline
from .. import models
from ..database import get_db


router = APIRouter(
    tags=["documents"]
)

@router.post("/ingest", status_code=status.HTTP_200_OK)
def ingest_documents(file: UploadFile = File(...), # this field is required (...), file path
                     db: Session = Depends(get_db), 
                     current_user = Depends(get_current_user)):


    print(f"Received file: {file.filename}")

    # Add the document to the document table
    document = models.Document(
        id = uuid4(),
        user_id = current_user.user_id,
        filename = file.filename,
        file_type = "pdf",
        processed = False
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    loaded_docs = pipeline.load_files(input_file=file)
    chunks = pipeline.chunk_files(loaded_docs)

    vectors = []
    for chunk in chunks:
        vector = pipeline.embedding(chunk) # get the embedding for each chunk
        vectors.append(vector) # list of vectors for each chunk
    
    print(f"Vector dimensions: {len(vector)}")
    print(type(vector))

    chunk_rows = []
    for i, chunk in enumerate(chunks):

        chunk_rows.append(
            models.DocumentChunks(
                id=uuid4(),
                document_id=document.id,
                chunk_idx=i,
                content=chunk.page_content,
                embedding=vectors[i],
                raw_text=chunk.page_content,
                metadata_={"source": f"{document.filename}_chunk_{i}"}
            )
        )

    if chunk_rows is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Error processing document chunks")

    print(chunk_rows[0]) # debugging

    db.add_all(chunk_rows)

    document.processed = True

    db.commit()

    return {
        "document_id": document.id,
        "file_name": document.filename,
        "chunks": len(chunk_rows)
    }

