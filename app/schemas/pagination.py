from sqlmodel import SQLModel


class PaginationParam(SQLModel):
    offset: int = 0
    limit: int = 100
