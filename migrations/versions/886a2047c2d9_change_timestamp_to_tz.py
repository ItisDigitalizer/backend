"""change_timestamp_to_tz

Revision ID: 886a2047c2d9
Revises: c08e2d85c506
Create Date: 2026-04-24 20:34:43.900522

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "886a2047c2d9"
down_revision: Union[str, Sequence[str], None] = "c08e2d85c506"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Меняем тип колонок на TIMESTAMP WITH TIME ZONE
    op.alter_column("users", "created_at", type_=sa.DateTime(timezone=True))
    op.alter_column("users", "updated_at", type_=sa.DateTime(timezone=True))

    op.alter_column(
        "document_templates", "created_at", type_=sa.DateTime(timezone=True)
    )
    op.alter_column(
        "document_templates", "updated_at", type_=sa.DateTime(timezone=True)
    )

    op.alter_column("template_fields", "created_at", type_=sa.DateTime(timezone=True))
    op.alter_column("template_fields", "updated_at", type_=sa.DateTime(timezone=True))

    op.alter_column(
        "generation_processes", "created_at", type_=sa.DateTime(timezone=True)
    )
    op.alter_column(
        "generation_processes", "updated_at", type_=sa.DateTime(timezone=True)
    )

    op.alter_column(
        "generated_documents", "created_at", type_=sa.DateTime(timezone=True)
    )
    op.alter_column(
        "generated_documents", "updated_at", type_=sa.DateTime(timezone=True)
    )


def downgrade():
    # Возвращаем обратно к TIMESTAMP WITHOUT TIME ZONE
    op.alter_column("users", "created_at", type_=sa.DateTime(timezone=False))
    op.alter_column("users", "updated_at", type_=sa.DateTime(timezone=False))

    op.alter_column(
        "document_templates", "created_at", type_=sa.DateTime(timezone=False)
    )
    op.alter_column(
        "document_templates", "updated_at", type_=sa.DateTime(timezone=False)
    )

    op.alter_column("template_fields", "created_at", type_=sa.DateTime(timezone=False))
    op.alter_column("template_fields", "updated_at", type_=sa.DateTime(timezone=False))

    op.alter_column(
        "generation_processes", "created_at", type_=sa.DateTime(timezone=False)
    )
    op.alter_column(
        "generation_processes", "updated_at", type_=sa.DateTime(timezone=False)
    )

    op.alter_column(
        "generated_documents", "created_at", type_=sa.DateTime(timezone=False)
    )
    op.alter_column(
        "generated_documents", "updated_at", type_=sa.DateTime(timezone=False)
    )
