from sqlalchemy import func, text
from sqlalchemy.dialects.postgresql import UUID

from .conn import db


class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    # accountId is missing
    name = db.Column(db.String(255))
    description = db.Column(db.Unicode)
    # created needs automated timestamp
    created = db.Column(db.DateTime, default=func.now())
    # Add relationship if required at some point


class Endpoint(db.Model):
    __tablename__ = 'endpoints'
    id = db.Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    account_id = db.Column(db.String(50), nullable=False, index=True)
    endpoint_type = db.Column(db.Integer(), nullable=False)
    name = db.Column(db.String(255))
    description = db.Column(db.Unicode)
    enabled = db.Column(db.Boolean(), nullable=False, default=False)

    # created needs automated timestamp
    created = db.Column(db.DateTime, default=func.now())
    updated = db.Column(db.DateTime, onupdate=func.now())


class WebhookEndpoint(db.Model):
    __tablename__ = 'endpoint_webhooks'
    id = db.Column(db.Integer(), primary_key=True, index=True)
    endpoint_id = db.Column(db.Integer(), db.ForeignKey("endpoints.id"))


class EmailSubscription(db.Model):
    __tablename__ = 'endpoint_email_subscriptions'
    account_id = db.Column(UUID, nullable=False, primary_key=True),
    user_id = db.Column(db.String(50), nullable=False, primary_key=True),
    event_type = db.Column(db.String(50), nullable=False, primary_key=True)
