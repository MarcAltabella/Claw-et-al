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
    
    docs_parsed = knowledge_pipeline.knowledge_parse(docs_dir)
    

    response_documents = []

    for document in docs_parsed:

        chunks_list = knowledge_pipeline.knowledge_splitter(doc_parsed=document)

        ## TO-DO EMBEDDINGS
    


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

        chunk_vectors = knowledge_pipeline.knowledge_vectors_chunks(chunks)

        chunk_rows = [
            models.Knowledge(
                id = uuid4(),
                user_id = current_user.user_id,
                document_id = document.id,
                chunk_idx = i,
                embedding = chunk_vectors[i],
                raw_text = chunk.page_content
            )
            for i, chunk in enumerate(chunks)
        ]   

        print(chunk_rows[0]) # debugging

        db.add_all(chunk_rows)
        document.processed = True
        db.commit()
        
        response_documents.append(
                {
                    "document_id": document.id,
                    "pdf_path_name": pdf_path.name,
                    "chunks": len(chunk_rows),
                    "processed": True,
                }
            )
        
    return {"Documents": response_documents}
    
    





    

