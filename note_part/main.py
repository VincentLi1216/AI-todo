import os
import json
from util_sumarization import batch_summarize
from util_meeting_todo import note_extract_todos
from util_tags import tag


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


if __name__ == '__main__':
    root_path = "/Users/USER/Desktop/Side_project/MindFlow-AI/note_part/data/TestingNote"
    file_path = "paper/Large Language Model based Multi-Agents- A Survey of Progress and Challenges.md"
    # file_path = "Meeting/第二次新型科技產品發想及進度追蹤-會議記錄.md"
    
    print(verify_and_initialize(root_path))
    
    print(batch_summarize(root_path))
    print(note_extract_todos(root_path, file_path))
    print(tag(root_path, file_path))