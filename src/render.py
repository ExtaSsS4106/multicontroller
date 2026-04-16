import eel
import os
from jinja2 import Environment, FileSystemLoader
from .settings import TEMPLATES
    
def render(file_path=None, data=None):
    try:
        env = Environment(loader=FileSystemLoader(TEMPLATES))
        template = env.get_template(file_path)
        if file_path and data:
            content = template.render(data)
            return content, data
        elif file_path and data == None:
            content = template.render()
            return content
        elif data and file_path == None:
            return data
        else:
            raise ValueError("Не переданы ни file_path, ни data") 
    except FileNotFoundError:
        print(f"Файл {file_path} не найден")
    except Exception as e:
        print("[error render]: ",e)       
