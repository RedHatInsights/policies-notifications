"""Create initial db

Revision ID: 8a70ac132b1f
Revises: 
Create Date: 2020-01-29 15:55:07.880970

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '8a70ac132b1f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'applications',
        sa.Column('id', UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Unicode(), nullable=True),
        sa.Column('created', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated', sa.DateTime(timezone=True), onupdate=func.now())
    )

    op.create_table(
        'endpoints',
        sa.Column('id', UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('account_id', sa.String(50), nullable=False, index=True),
        sa.Column('endpoint_type', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, default=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Unicode(), nullable=True),
        sa.Column('created', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated', sa.DateTime(timezone=True), onupdate=func.now())
    )

    # Could use JSON field in the endpoints table also for properties..
    op.create_table(
        'endpoint_webhooks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('endpoint_id', UUID(), nullable=False, index=True),
        sa.Column('url', sa.Unicode(), nullable=False),
        sa.Column('method', sa.String(10), nullable=False),  # We could use enum numbering
        sa.Column('disable_ssl_verification', sa.Boolean(), nullable=False, default=False),
        sa.Column('secret_token', sa.String(255), nullable=True),
        sa.Column('payload_transformer', sa.String(50), nullable=True)
    )

    op.create_table(
        'endpoint_email_subscriptions',
        sa.Column('account_id', sa.String(50), nullable=False, primary_key=True),
        sa.Column('user_id', sa.String(50), nullable=False, primary_key=True),
        sa.Column('event_type', sa.String(50), nullable=False, primary_key=True)
        # sa.UniqueConstraint('account_id', 'user_id', 'event_type', name='unique_subscription_IX')
    )

    op.create_table(
        'email_aggregation',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('account_id', sa.String(50), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('payload', JSONB, nullable=False),
        #     Needs to be an index of account_id + created as that's the search query
        sa.Index('IX_time_search_account_mails', 'account_id', 'created')
    )


def downgrade():
    op.drop_table('applications')
    op.drop_table('endpoints')
    op.drop_table('endpoint_webhooks')
    op.drop_table('endpoint_email_subscriptions')
    op.drop_table('email_aggregation')
