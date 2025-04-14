# Running Tests

Current status of units tests:

[![Unit Tests](https://github.com/Christopher-K-Long/thread-chunks/actions/workflows/test-python-package.yml/badge.svg)](https://github.com/Christopher-K-Long/thread-chunks/actions/workflows/test-python-package.yml)

You can run the unit tests yourself using [pytest](https://docs.pytest.org) or [tox](https://tox.wiki/).

## Using [tox](https://tox.wiki/)

Once [tox](https://tox.wiki/) is installed you can execute the command
```bash
tox
```
in from a terminal in the root directory of thread-chunks to execute the tests for your installed python interpreter.

## Using [pytest](https://docs.pytest.org)

To execute the tests with [pytest](https://docs.pytest.org) you will need to set up a python environment with thread-chunks and the packages in `texts/requirements.txt`. For example, you can run
```bash
pip install ./
pip install tests/requirements.txt
```
from the root directory of thread-chunks to install all the requirements. Next the tests can be executed with the command
```bash
pytest
```
from the root directory of thread-chunks.

---

[Previous](actors.md)