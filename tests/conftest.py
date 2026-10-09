import os

# Must be set before `app` (and its config) is imported anywhere, and before
# python-dotenv's load_dotenv(".flaskenv") runs, since that call does not
# override already-set environment variables.
os.environ.setdefault(
    'DATABASE_URL',
    os.environ.get('TEST_DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/touchline_test')
)
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('AZURE_STORAGE_ACCOUNT_NAME', 'test-account')
os.environ.setdefault('AZURE_STORAGE_ACCOUNT_KEY', 'dGVzdC1rZXk=')
os.environ.setdefault('AZURE_CONTAINER_NAME', 'test-container')

import pytest
import app as app_module
from app.models.db import db


@pytest.fixture()
def app():
    flask_app = app_module.app
    flask_app.config.update(TESTING=True)
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def make_user(app):
    from app.models.user_model import User

    def _make_user(username='testuser', password='password123'):
        success, user = User.register_user(username, password)
        assert success, user
        return user

    return _make_user
