import pytest

from lokii import Lokii


@pytest.fixture(scope="module")
def setup_session_env(request):
    Lokii.setup_env()

    def teardown():
        Lokii.clean_env(force=True)

    request.addfinalizer(teardown)
