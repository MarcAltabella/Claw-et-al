from uuid import uuid4
from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session
from ..oauth2 import get_current_user
from .. import models, schemas
from ..database import get_db
from ..rag import knowledge_pipeline
from pathlib import Path



router = APIRouter(
    tags=["knowledge"],
    prefix="/knowledge"
)

# UPLOAD KNOWLEDGE TO THE DB
@router.post("/upload_knowledge", status_code=status.HTTP_200_OK)
def feed_knowledge(documents_path: schemas.KnowlegeLoad,
                   db: Session = Depends(get_db),
                   current_user = Depends(get_current_user)):

    docs_dir = Path(documents_path.documents_path)
    
    docs_loaded = knowledge_pipeline.knowledge_load(docs_dir) # Chunks included

    for pdf_path, chunks in docs_loaded:

        document = models.Document(
            id = uuid4(),
            user_id = current_user.user_id,
            filename = pdf_path.name,
            file_type = "pdf",
            processed = False
        )

        db.add(document)
        db.commit()
        db.refresh(document)

    docs_vectors = knowledge_pipeline.knowledge_vectors(docs_loaded)

    chunk_rows = [
        models.Knowledge(
            id = uuid4(),
            user_id = current_user.user_id,
            document_id = document.id,
            chunk_idx = i,
            embedding = docs_vectors[i],
            raw_text = chunk.page_content
        )
    for i, chunk in enumerate(docs_loaded)
]   

    print(chunk_rows[0]) # debugging

    db.add_all(chunk_rows)
    document.processed = True
    db.commit()


    return {
        "Documents": [
            {
                "document_id": document.id,
                "chunks": len(chunk_rows),
                "processed": True,
            }
            for i, loaded_doc in enumerate(docs_loaded)
        ]
    }
    
    





    

