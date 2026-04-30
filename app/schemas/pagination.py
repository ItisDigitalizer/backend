from sqlmodel import SQLModel


class PaginationParam(SQLModel):
    skip: int = 0
    limit: int = 100
