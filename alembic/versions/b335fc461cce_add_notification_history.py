"""Add notification history

Revision ID: b335fc461cce
Revises: bc6e3f6ca645
Create Date: 2020-05-11 14:01:34.888686

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b335fc461cce'
down_revision = 'bc6e3f6ca645'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'notification_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('account_id', sa.String(length=50), nullable=False),
        sa.Column('endpoint_id', postgresql.UUID(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('invocation_time', sa.Integer(), nullable=False),
        sa.Column('invocation_result', sa.Boolean(), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['endpoint_id'], ['endpoints.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('IX_account_endpoint_search', 'notification_history', ['account_id', 'endpoint_id'], unique=False)


def downgrade():
    op.drop_index('IX_account_endpoint_search', table_name='notification_history')
    op.drop_table('notification_history')
