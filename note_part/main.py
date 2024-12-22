import os
import json
from util_sumarization import summarize

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


def bacth_summarize(root_path):
    """
    Batch process all the Markdown files in the provided directory and generate summaries for each file.
    
    :param root_path: The root directory containing the Markdown files.
    :return: A message indicating the completion of the summarization process.
    """
    if 'summary.json' not in os.listdir(os.path.join(root_path, '.mindflow')):
        print("Creating the summary.json file...")
        with open(os.path.join(root_path, '.mindflow', 'summary.json'), 'w') as f:
            f.write("{}")
    
    md_files = list_md_files(root_path)
    summaries = {'root': root_path, 'data': []}
    for file_path in md_files:
        summaries['data'].append(
            {
                'path': file_path['relative_path'],
                'text': summarize(file_path['absolute_path'])
            }
        )
        
    with open(os.path.join(root_path, '.mindflow', 'summary.json'), 'w') as f:
        f.write(json.dumps(summaries))
    
    return "Summarization completed successfully."


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


def run(root_path):
    print(verify_and_initialize(root_path))
    print(bacth_summarize(root_path))
    return "Process completed successfully."

if __name__ == '__main__':
    root_path = "/Users/USER/Desktop/Side_project/MindFlow-AI/note_part/data/TestingNote"
    print(run(root_path))