# How to run tests

The tests assume that the project is installed as a package when importing.
An [editable install](https://pip.pypa.io/en/stable/topics/local-project-installs/)
is a good way to achieve this. The used package/project manager, [uv](https://docs.astral.sh/uv/),
creates an editable install automatically: by running

> uv run pytest

installation of a venv with the required packages should happen,
and the tests be run.