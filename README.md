# Set up UV
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Prep project
```Command
uv venv

.venv\Scripts\activate.bat

uv tool install pip

uv pip install pyside6

uv pip install SQLAlchemy configparser pre-commit

uv pip install black mypy

uv pip compile --output-file=requirements.txt pyproject.toml

uv pip install -r requirements.txt

pre-commit install

python src/main.py
```


## 🧹 Format & Type Check

```bash
uv pip install black mypy
black src/
mypy src/
```
