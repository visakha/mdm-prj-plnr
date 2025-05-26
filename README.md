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


# VSCode HotKeys
## Note pay attn to upper case vs lower case
Select and widen by indent <alt><shft><right arrow>,  do the reverse <left arrow>.  
Recently used is <ctrl> e  
Navigate to Explorer (left pane) <ctrl> E  
Close Nav pane <ctrl> b  | <ctrl> B  
Close window <ctrl> W  

