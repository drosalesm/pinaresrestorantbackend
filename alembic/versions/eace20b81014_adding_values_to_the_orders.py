"""adding values to the orders

Revision ID: eace20b81014
Revises: 0cb74969761e
Create Date: 2025-04-24 07:20:50.318496
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'eace20b81014'
down_revision: Union[str, None] = '0cb74969761e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(), nullable=True))
        batch_op.drop_column('user_id')  # Drop the FK column


def downgrade() -> None:
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_orders_user_id_users', 'users', ['user_id'], ['id'])
        batch_op.drop_column('username')
