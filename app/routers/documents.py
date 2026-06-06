import os

from uuid import uuid4
from fastapi import HTTPException, status, Depends, APIRouter, UploadFile, File
from sqlalchemy.orm import Session
from ..oauth2 import get_current_user
from ..rag import pipeline
from .. import models
from ..database import get_db


router = APIRouter(
    tags=["documents"],
    prefix="/documents"
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
        "Document_id": document.id,
        "File_name": document.filename,
        "Chunks": len(chunk_rows)
    }


@router.get("/", status_code=status.HTTP_200_OK)
def get_documents(db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    documents = db.query(models.Document).filter(models.Document.user_id == current_user.user_id).all()

    if not documents:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Documents for user {current_user.user_id} not found")

    return {
        "Documents": [
            {   
                "Document ID": document.id,
                "Document name": document.filename,
                "Document type": document.file_type,
                "Processed": document.processed
            }
            for document in documents
        ]
    }

# Get document chunks for a document
@router.get("/{document_id}", status_code=status.HTTP_200_OK)
def get_document_ind(document_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    document = db.query(models.Document).filter(models.Document.id == document_id, 
                                                models.Document.user_id == current_user.user_id).first()

    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    chunks = db.query(models.DocumentChunks).filter(models.DocumentChunks.document_id == document_id).all()

    return {
        "Documents": [
            {
                "document_id": document.id,
                "file_name": document.filename,
                "processed": document.processed
            }
        ],
        "Chunks": [
            {
                "chunk_id": chunk.id,
                "chunk_idx": chunk.chunk_idx,
                "content": chunk.content,
                "embedding_preview": str(chunk.embedding)[:100]
            }
            for chunk in chunks
        ]
    }


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(document_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):

    document = db.query(models.Document).filter(models.Document.id == document_id, 
                                                models.Document.user_id == current_user.user_id).first()

    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    db.query(models.DocumentChunks).filter(models.DocumentChunks.document_id == document_id).delete()
    db.delete(document)
    db.commit()

    return {"detail": "Document and associated chunks deleted successfully"}