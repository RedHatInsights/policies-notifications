import pytest
from alembic import command
from alembic.config import Config
from starlette.config import environ

# This should cause an error if we run in the wrong order
environ['TESTING'] = 'TRUE'

# from app.main import notif_app
from app.core.config import DATABASE_URL


@pytest.fixture(scope="module", autouse=True)
def create_and_destroy_test_database():
    config = Config("alembic.ini")   # Run the migrations.
    config.set_main_option('sqlalchemy.url', str(DATABASE_URL))
    command.upgrade(config, "head")
    yield  # Run tests
    command.downgrade(config, "8a70ac132b1f")
    command.downgrade(config, "-1")


# @pytest.fixture(scope="session", autouse=True)
# def client():
#     with TestClient(notif_app) as test_client:
#         yield test_client
