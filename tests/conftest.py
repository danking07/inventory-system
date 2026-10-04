import copy
import os
import sys

import pytest

# Let the tests import app.py from the project folder
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import app as app_module  # noqa: E402

# Remember the starting data so every test can begin from it
SEED = copy.deepcopy(app_module.inventory)


@pytest.fixture
def client():
    """A fake browser for calling the API, with fresh data for each test."""
    app_module.inventory[:] = copy.deepcopy(SEED)
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()