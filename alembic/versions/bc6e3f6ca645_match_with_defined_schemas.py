"""Match with defined schemas

Revision ID: bc6e3f6ca645
Revises: 8a70ac132b1f
Create Date: 2020-05-11 13:54:00.170534

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc6e3f6ca645'
down_revision = '8a70ac132b1f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key('FK_endpoint_id_webhooks', 'endpoint_webhooks', 'endpoints', ['endpoint_id'], ['id'],
                          ondelete='CASCADE')
    op.drop_column('endpoint_webhooks', 'payload_transformer')


def downgrade():
    op.add_column('endpoint_webhooks', sa.Column('payload_transformer', sa.VARCHAR(length=50), autoincrement=False,
                                                 nullable=True))
    op.drop_constraint('FK_endpoint_id_webhooks', 'endpoint_webhooks', type_='foreignkey')
