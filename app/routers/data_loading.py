import os

from uuid import uuid4
from fastapi import HTTPException, status, Depends, APIRouter, UploadFile, File
from sqlalchemy.orm import Session
from .. import get_current_user
from ..rag import pipeline
from .. import models
from ..database import get_db


routers = APIRouter(
    tags=["documents"]
)

@routers.post("/documents/ingest", status_code=status.HTTP_200_OK)
def ingest_documents(file: UploadFile = File(...), # this field is required (...), file path
                     db: Session = Depends(get_db), 
                     current_user = Depends(get_current_user)):

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

    loaded_docs = pipeline.load_files(file)
    chunks = pipeline.chunk_files(loaded_docs)
    vectors = pipeline.embedding(chunks)

    chunk_rows = []
    for i, (chunk) in enumerate(chunks):

        chunk_rows.append(
            models.DocumentChunks(
                id=uuid4(),
                document_id=document.id,
                chunk_idx=i,
                content=chunk.page_content,
                embedding=vectors[i],
                raw_text=chunk.page_content,
                metadata_={}
            )
        )

    db.add_all(chunk_rows)

    document.processed = True

    db.commit()

    return {
        "document_id": document.id,
        "file_name": document.filename,
        "chunks": len(chunk_rows)
    }

    

