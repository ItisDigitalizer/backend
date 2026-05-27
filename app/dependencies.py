from typing import Annotated

from fastapi.params import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
from app.schemas.generation_process import GenerationProcessFilters
from app.services.auth_service import AuthService
from app.services.document_template_service import DocumentTemplateService
from app.services.generated_document_service import GeneratedDocumentService
from app.services.generation_process_service import GenerationProcessService
from app.services.document_generator_service import DocumentGeneratorService
from app.services.template_field_service import TemplateFieldService
from app.services.user_service import UserService

SessionDep = Annotated[AsyncSession, Depends(get_session)]

UserServiceDep = Annotated[UserService, Depends(UserService)]

GeneratedDocumentServiceDep = Annotated[
    GeneratedDocumentService, Depends(GeneratedDocumentService)
]

GenerationProcessServiceDep = Annotated[
    GenerationProcessService, Depends(GenerationProcessService)
]

DocumentTemplateServiceDep = Annotated[
    DocumentTemplateService, Depends(DocumentTemplateService)
]

TemplateFieldServiceDep = Annotated[TemplateFieldService, Depends(TemplateFieldService)]

AuthServiceDep = Annotated[AuthService, Depends(AuthService)]

GenerationProcessFiltersDep = Annotated[
    GenerationProcessFilters, Depends(GenerationProcessFilters)
]
DocumentGeneratorServiceDep = Annotated[
    DocumentGeneratorService, Depends(DocumentGeneratorService)
]
