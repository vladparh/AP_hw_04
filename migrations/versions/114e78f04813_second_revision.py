"""Second revision

Revision ID: 114e78f04813
Revises: f3a497e844b7
Create Date: 2024-03-12 11:58:16.281378

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '114e78f04813'
down_revision = 'f3a497e844b7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mushroom',
    sa.Column('id', sa.Integer(), nullable=True),
    sa.Column('Info', sa.JSON(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('mushroom')
    # ### end Alembic commands ###
