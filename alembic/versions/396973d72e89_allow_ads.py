"""allow ads

Revision ID: 396973d72e89
Revises: 065483793c10
Create Date: 2024-09-16 16:02:43.941832

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_storages.integrations.sqlalchemy
from fastapi_storages import FileSystemStorage

# revision identifiers, used by Alembic.
revision: str = '396973d72e89'
down_revision: Union[str, None] = '065483793c10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ads',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('image', fastapi_storages.integrations.sqlalchemy.FileType(storage=FileSystemStorage("uploads")), nullable=True),
    sa.Column('url', sa.String(length=1024), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ads')
    # ### end Alembic commands ###
