"""adding isv value

Revision ID: 0cb74969761e
Revises: d314cfdc08a4
Create Date: 2025-04-22 10:40:36.588688

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0cb74969761e'
down_revision: Union[str, None] = 'd314cfdc08a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('billingConfig',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('isv', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_billingConfig_id'), 'billingConfig', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_billingConfig_id'), table_name='billingConfig')
    op.drop_table('billingConfig')
    # ### end Alembic commands ###
