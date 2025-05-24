import os
import json

def import_json(base_folder="predictions_LSTM", output_file="predicted_products.json"):
    all_products = []

    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(script_dir, base_folder)

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        all_products.append(data)
                except Exception as e:
                    print(f"Помилка з {file_path}: {e}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print(f"✅ Збережено {len(all_products)} продуктів у '{output_file}'")
