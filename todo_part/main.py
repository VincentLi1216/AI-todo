import things
import json

data = things.todos()
print(len(data))
print(data[0])


def save_json(data, file_path):
    """
    將給定的 JSON 資料儲存到指定的文件路徑。
    
    :param data: 要儲存的 JSON 資料（通常是 Python 字典或列表）。
    :param file_path: 儲存 JSON 文件的路徑。
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"資料已成功儲存到 {file_path}")
    except Exception as e:
        print(f"儲存資料時發生錯誤: {e}")


save_json(data, "./todos.json")

# print(things.tags())
