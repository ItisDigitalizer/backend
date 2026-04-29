from typing import Annotated

from fastapi.params import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.repositories.document_template_repo import DocumentTemplateRepository
from app.repositories.generated_document_repo import GeneratedDocumentRepository
from app.repositories.generation_process_repo import GenerationProcessRepository
from app.repositories.template_field_repo import TemplateFieldRepository
from app.repositories.user_repo import UserRepository
from app.services.document_template_service import DocumentTemplateService
from app.services.generated_document_service import GeneratedDocumentService
from app.services.generation_process_service import GenerationProcessService
from app.services.template_field_service import TemplateFieldService
from app.services.user_service import UserService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_generated_document_repository(
    session: SessionDep,
) -> GeneratedDocumentRepository:
    return GeneratedDocumentRepository(session)


def get_generated_document_service(
    repository: GeneratedDocumentRepository = Depends(
        get_generated_document_repository
    ),
) -> GeneratedDocumentService:
    return GeneratedDocumentService(repository)


GeneratedDocumentServiceDep = Annotated[
    GeneratedDocumentService, Depends(get_generated_document_service)
]


def get_generation_process_repository(
    session: SessionDep,
) -> GenerationProcessRepository:
    return GenerationProcessRepository(session)


def get_generation_process_service(
    repository: GenerationProcessRepository = Depends(
        get_generation_process_repository
    ),
) -> GenerationProcessService:
    return GenerationProcessService(repository)


GenerationProcessServiceDep = Annotated[
    GenerationProcessService, Depends(get_generation_process_service)
]


def get_document_template_repository(
    session: SessionDep,
) -> DocumentTemplateRepository:
    return DocumentTemplateRepository(session)


def get_document_template_service(
    repository: DocumentTemplateRepository = Depends(get_document_template_repository),
) -> DocumentTemplateService:
    return DocumentTemplateService(repository)


DocumentTemplateServiceDep = Annotated[
    DocumentTemplateService, Depends(get_document_template_service)
]


def get_template_field_repository(session: SessionDep) -> TemplateFieldRepository:
    return TemplateFieldRepository(session)


def get_template_field_service(
    repository: TemplateFieldRepository = Depends(get_template_field_repository),
) -> TemplateFieldService:
    return TemplateFieldService(repository)


TemplateFieldServiceDep = Annotated[
    TemplateFieldService, Depends(get_template_field_service)
]
