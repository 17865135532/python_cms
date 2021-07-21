import pytest

from application import create_app


@pytest.fixture
def app():
    app = create_app()
    ctx = app.test_request_context()
    with ctx:
        yield app


@pytest.fixture
def client(app):
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client
