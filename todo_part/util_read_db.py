import things
import json

# data = things.todos()
# print(len(data))
# print(data[0])


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


def get_things_areas_names():
    """
    獲取 Things 中所有區域的名稱。
    
    :return: 一個包含所有區域名稱的列表。
    """
    
    areas = things.areas()

    area_names = [area['title'] for area in areas]

    return area_names

def get_things_projects_names():
    """
    獲取 Things 中所有區域的名稱。
    
    :return: 一個包含所有區域名稱的列表。
    """
    
    projects = things.projects()

    project_names = [project['title'] for project in projects]

    return project_names


if __name__ == "__main__":
    pass
    # print(things.todos())
    # print(things.today())
    # print(things.tags())
    # print(things.lists())
    print(things.areas())
    print(things.projects())
    print(get_things_areas_names())
    print(get_things_projects_names())
    # print(things.checklists())
    # print(things.headings
