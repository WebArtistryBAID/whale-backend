"""user points

Revision ID: 3093b75b15a7
Revises: c6a4747e2c5b
Create Date: 2024-09-22 18:55:34.823486

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import fastapi_storages.integrations.sqlalchemy



# revision identifiers, used by Alembic.
revision: str = '3093b75b15a7'
down_revision: Union[str, None] = 'c6a4747e2c5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('points', sa.DECIMAL(precision=5, scale=2), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'points')
    # ### end Alembic commands ###
