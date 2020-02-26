from sqlalchemy import func, text
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .conn import db


class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    # accountId is missing
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Unicode)
    # created needs automated timestamp
    created = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated = db.Column(db.DateTime, default=func.now())
    # Add relationship if required at some point


class Endpoint(db.Model):
    __tablename__ = 'endpoints'
    id = db.Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    account_id = db.Column(db.String(50), nullable=False, index=True)
    endpoint_type = db.Column(db.Integer(), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Unicode)
    enabled = db.Column(db.Boolean(), nullable=False, default=False)

    # created needs automated timestamp
    created = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=func.now())


class WebhookEndpoint(db.Model):
    __tablename__ = 'endpoint_webhooks'
    id = db.Column(db.Integer(), primary_key=True)
    endpoint_id = db.Column(db.Integer(), db.ForeignKey("endpoints.id"), nullable=False, index=True)
    url = db.Column(db.Unicode(), nullable=False)
    method = db.Column(db.String(6), nullable=False)
    disable_ssl_verification = db.Column(db.Boolean(), nullable=False, default=False)
    secret_token = db.Column(db.String(), nullable=True)
    # payload_transformer = db.Column(db.String(50), nullable=True)


class EmailSubscription(db.Model):
    __tablename__ = 'endpoint_email_subscriptions'
    account_id = db.Column(db.String(50), nullable=False, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False, primary_key=True)


class EmailAggregation(db.Model):
    __tablename__ = 'email_aggregation'
    id = db.Column(db.Integer(), primary_key=True)
    account_id = db.Column(db.String(50), nullable=False)
    insight_id = db.Column(db.String(50), nullable=False)
    created = db.Column(db.DateTime, default=func.now(), nullable=False)
    payload = db.Column(JSONB, nullable=False)

    @db.declared_attr
    def ix_time_search_account_mails(cls):
        return db.Index('IX_time_search_account_mails', 'account_id', 'created')


class NotificationHistory(db.Model):
    __tablename__ = 'notification_history'
    id = db.Column('id', db.Integer(), primary_key=True)
    account_id = db.Column('account_id', db.String(50), nullable=False)
    endpoint_id = db.Column('endpoint_id', UUID(), db.ForeignKey("endpoints.id"), nullable=False)
    created = db.Column("created", db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    invocation_time = db.Column("invocation_time", db.Integer(), nullable=False)  # Time in milliseconds
    invocation_result = db.Column("invocation_result", db.Boolean(), nullable=False, default=False)
    details = db.Column('details', JSONB(), nullable=True)

    @db.declared_attr
    def ix_account_endpoint_search(cls):
        return db.Index('IX_account_endpoint_search', 'account_id', 'endpoint_id')
