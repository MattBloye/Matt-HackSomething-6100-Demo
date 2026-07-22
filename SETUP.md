PREREQUISITES (do once)
1. Install Python 3.12   | winget install Python.Python.3.12
   -> then CLOSE and REOPEN PowerShell (so it picks up Python)
2. Install Ollama        | download from https://ollama.com and install
3. Pull the models:
      ollama pull nomic-embed-text
      ollama pull qwen2.5:7b-instruct
   -> confirm with: ollama list

SET UP THE PROJECT
4. Unzip the project, then open the folder in VS Code
5. Open a terminal IN that folder (VS Code: Terminal > New Terminal), or:
      cd C:\path\to\prompt-injection-lab
6. Create the environment   | py -3.12 -m venv .venv
7. Activate it              | .\.venv\Scripts\Activate.ps1
      (if blocked: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass, then retry)
8. Upgrade pip             | python -m pip install --upgrade pip
9. Install requirements    | pip install -r requirements.txt

RUN IT (two terminals, both with .venv activated)
10. Terminal A:  python listener.py     (leave running)
11. Terminal B:  python ingest.py
12. Terminal B:  python run_attack.py    -> watch Terminal A for stolen data
13. Terminal B:  python run_defended.py  -> attack now blocked