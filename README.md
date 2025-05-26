# Set up UV
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Prep project
```Command
uv venv
.venv\Scripts\activate.bat
uv tool install pip
uv pip compile --output-file=requirements.txt pyproject.toml
uv pip install -r requirements.txt
pre-commit install
python src/main_app.py
```


## 🧹 Format & Type Check

```bash
uv pip install black mypy
black src/
mypy src/
```


# VSCode HotKeys
## Note pay attn to upper case vs lower case
Note: add two spaces at the end of each line to force a 'New Line' Render
Select and widen by indent <alt><shft><right arrow>,  do the reverse <left arrow>.  
Recently used is <ctrl> e  
Navigate to Explorer (left pane) <ctrl> E  
Close Nav pane <ctrl> b  | <ctrl> B  
Close window <ctrl> W  

# Screenshots

Branch1  pic1 ![Inital home page](readme-res/pics/ini-home-pg.png)  

# Branches

## Branch 001
```text
    commit msg: done- good state, close branch 001
    code written by Google Gemini. the prompt file is not uploaded to this project here.
    it did a decent job.
    to fix: the Add Phase, Add Epic and Add Task are not showing a dialog box to add the item name, desc, assigned to, status and due date
        once the user adds the inputs, it should add it to the approp hierarchy and persist to the DB
```

## Branch 002
```text
    prompt: 
    modify the functionality of the buttons Add Phase, Add Epic and Add Task. these buttons should open a dialog box for the task
        The shape of the task is same as the Model Task
        once the user adds the inputs the task, it should add it to the appropriate hierarchy and persist to the DB
```
