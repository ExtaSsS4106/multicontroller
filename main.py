import eel, json
from src.settings import *

try:
    with open(CONF_PATH, 'r', encoding='utf-8') as file:
        page = json.load(file)
except:
    page = {"load_page": "login"}
    with open(CONF_PATH, 'w', encoding='utf-8') as f:
        json.dump(page, f, indent=4, ensure_ascii=False)

eel.init("web")


if __name__ == "__main__":
    from src.views import Views
    eel.start("pages/index.html", size=(1900, 1000), port=0)