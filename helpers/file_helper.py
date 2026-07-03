import json
import os

class FileHelper:
    @staticmethod
    def load_json(filepath: str) -> dict:
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return None

    @staticmethod
    def save_file(filepath: str, content: str):
        out_dir = os.path.dirname(filepath)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
