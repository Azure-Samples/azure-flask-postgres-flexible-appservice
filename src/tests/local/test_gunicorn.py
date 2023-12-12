import sys
from unittest import mock

import pytest
from gunicorn.app.wsgiapp import run


def test_config_imports():
    argv = ["gunicorn", "--check-config", "flaskapp:create_app()", "-c", "src/gunicorn.conf.py"]

    with mock.patch.object(sys, "argv", argv):
        with pytest.raises(SystemExit) as excinfo:
            run()

    assert excinfo.value.args[0] == 0
