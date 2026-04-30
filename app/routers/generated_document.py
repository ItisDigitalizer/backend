from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends

from app.dependencies import GeneratedDocumentServiceDep
from app.models.generated_document import (
    GeneratedDocumentCreate,
    GeneratedDocumentRead,
    GeneratedDocumentUpdate,
)
from app.schemas.generated_document import GeneratedDocumentFilters
from app.schemas.pagination import PaginationParam

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "/", response_model=GeneratedDocumentRead, status_code=status.HTTP_201_CREATED
)
async def create_document(
    document_data: GeneratedDocumentCreate, service: GeneratedDocumentServiceDep
):
    """Создание нового документа"""
    try:
        document = await service.create_document(document_data)
        return document
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[GeneratedDocumentRead])
async def get_documents(
    service: GeneratedDocumentServiceDep,
    pagination: PaginationParam = Depends(),
    gen_process_id: UUID | None = None,
) -> Any:
    """Получение списка документов с фильтрацией по процессу"""
    filters = GeneratedDocumentFilters(gen_process_id=gen_process_id)
    return await service.get_filtered_document(
        filters, pagination.skip, pagination.limit
    )


@router.get("/{document_id}", response_model=GeneratedDocumentRead)
async def get_document(document_id: UUID, service: GeneratedDocumentServiceDep) -> Any:
    """Получение документа по ID"""
    document = await service.get(document_id)  # type: ignore
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return document


@router.patch("/{document_id}", response_model=GeneratedDocumentRead)
async def update_document(
    document_id: UUID,
    updates: GeneratedDocumentUpdate,
    service: GeneratedDocumentServiceDep,
):
    """Обновление документа"""
    document = await service.update_document(document_id, updates)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: UUID, service: GeneratedDocumentServiceDep):
    """Удаление документа"""
    document = await service.delete_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return None


@router.delete("/by-process/{gen_process_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_documents_by_process(
    gen_process_id: UUID, service: GeneratedDocumentServiceDep
):
    """Удаление всех документов процесса"""
    deleted_count = await service.delete_by_process_id(gen_process_id)
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No documents found for this process",
        )
    return None
