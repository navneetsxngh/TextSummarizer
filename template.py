import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format= '[ %(asctime)s - %(message)s ]')

PROJECT_NAME = "textsummarizer"

list_of_files=[
    f".github/workflows/.gitkeep",
    f"src/{PROJECT_NAME}/__init__.py",
    f"src/{PROJECT_NAME}/entity/__init__.py",
    f"src/{PROJECT_NAME}/entity/config_entity.py",
    f"src/{PROJECT_NAME}/components/__init__.py",
    f"src/{PROJECT_NAME}/utils/__init__.py",
    f"src/{PROJECT_NAME}/utils/main.py",
    f"src/{PROJECT_NAME}/config/__init__.py",
    f"src/{PROJECT_NAME}/config/configuration.py",
    f"src/{PROJECT_NAME}/pipeline/__init__.py",
    f"src/{PROJECT_NAME}/constants/__init__.py",
    f"src/{PROJECT_NAME}/logging/__init__.py",
    f"config/config.yaml",
    f"params.yaml",
    f"schema.yaml",
    f"main.py",
    f"Dockerfile",
    f"requirements.txt",
    f"setup.py",
    f"research/research.ipynb",
    f"templates/index.html",
    f"app.py"
]

for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating Directory {filedir} for the file {filename}")
    
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, 'w') as f:
            pass
        logging.info(f"Creating Empty File: {filepath}")

    else:
        logging.info(f"{filename} is already exist")