import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

HOST="http://127.0.0.1:8010/"
CONF_PATH = "configs/conf.json"
USER_DATA = "configs/user_data.json"
TEMPLATES = os.path.join(BASE_DIR, 'web/pages/templates')