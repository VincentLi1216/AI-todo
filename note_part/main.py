import os
import json
from util_sumarization import summarize
from util_meeting_todo import extract_todos


def verify_and_initialize(root_path):
    """
    Verify the directory structure and initialize the necessary directories for the MindFlow AI tool.
    
    :param root_path: The root directory of the Obsidian project.
    :return: A message indicating the completion of the initialization process.
    """
    if '.obsidian' not in os.listdir(root_path):
        raise "Could not find the Obsidian project in the provided directory."
    
    if '.mindflow' not in os.listdir(root_path):
        print("Creating the .mindflow directory...")
        os.mkdir(os.path.join(root_path, '.mindflow'))
    
    return "Initialization completed successfully."


def list_md_files(directory):
    """
    List all the Markdown files in the provided directory and its subdirectories.
    
    :param directory: The directory to search for Markdown files.
    :return: A list of dictionaries containing the absolute and relative paths of the Markdown files.
    """
    md_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_files.append({
                    "absolute_path": os.path.join(root, file),
                    "relative_path": os.path.relpath(os.path.join(root, file), directory)
                })
    return md_files


def test_note_batch_summarize(root_path):
    """
    Batch process all the Markdown files in the provided directory and generate summaries for each file.
    
    :param root_path: The root directory containing the Markdown files.
    :return: A message indicating the completion of the summarization process.
    """
    if 'summary.json' not in os.listdir(os.path.join(root_path, '.mindflow')):
        print("Creating the summary.json file...")
        summaries = {'root': root_path, 'data': []}
        with open(os.path.join(root_path, '.mindflow', 'summary.json'), 'w') as f:
            f.write(json.dumps(summaries))
    else:
        with open(os.path.join(root_path, '.mindflow', 'summary.json'), 'r') as f:
            summaries = json.load(f)
    
    md_files = list_md_files(root_path)
    
    for file_path in md_files:
        summaries['data'].append(
            {
                'path': file_path['relative_path'],
                'text': summarize(file_path['absolute_path'])
            }
        )
        
    with open(os.path.join(root_path, '.mindflow', 'summary.json'), 'w') as f:
        f.write(json.dumps(summaries))
    
    return "Process completed successfully."


def test_note_extract_todos(root_path, file_path):
    if 'todo.json' not in os.listdir(os.path.join(root_path, '.mindflow')):
        print("Creating the todo.json file...")
        todos = {'root': root_path, 'file': [], 'data': []}
        with open(os.path.join(root_path, '.mindflow', 'todo.json'), 'w') as f:
            f.write(json.dumps(todos))
    else:
        with open(os.path.join(root_path, '.mindflow', 'todo.json'), 'r') as f:
            todos = json.load(f)
    
    if file_path not in todos['file']:
        todos['file'].append(file_path)
    else:
        return "To-do items for this file have already been extracted."
    
    results = extract_todos(os.path.join(root_path, file_path))
    for todo in results:
        todo = todo.__dict__
        todo['source'] = file_path
        todo['completion_time'] = todo['completion_time'].isoformat()
        todos['data'].append(todo)
        
    with open(os.path.join(root_path, '.mindflow', 'todo.json'), 'w') as f:
        f.write(json.dumps(todos))
    
    return "Process completed successfully."


if __name__ == '__main__':
    root_path = "/Users/USER/Desktop/Side_project/MindFlow-AI/note_part/data/TestingNote"
    file_path = "Meeting/第二次新型科技產品發想及進度追蹤-會議記錄.md"
    
    print(verify_and_initialize(root_path))
    
    # print(test_note_batch_summarize(root_path))
    print(test_note_extract_todos(root_path, file_path))