import os, sys
from fastapi.testclient import TestClient
import pytest


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from main import app

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
