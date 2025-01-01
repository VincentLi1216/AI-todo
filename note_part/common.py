import os
import json
import hashlib

def get_hash(input_string: str, algorithm: str = 'sha256') -> str:
    hash_object = hashlib.new(algorithm)
    hash_object.update(input_string.encode('utf-8'))
    return hash_object.hexdigest()

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

def get_summary(root_path: str, file_path: str) -> str:
    """
    Load the summary of a specific Markdown file.
    
    :param root_path: The root directory containing the Markdown files.
    :param file_path: The relative path of the Markdown file to retrieve the summary from.
    :return: The summarized text.
    """
    with open(os.path.join(root_path, '.mindflow', 'summary.json'), 'r') as f:
        summaries = json.load(f)
    
    return summaries['data'][get_hash(file_path)]['text']

def get_tags(root_path: str, file_path: str) -> list:
    """
    Load the tags of a specific Markdown file.
    
    :param root_path: The root directory containing the Markdown files.
    :param file_path: The relative path of the Markdown file to retrieve the tags from.
    :return: The list of tags associated with the Markdown file.
    """
    with open(os.path.join(root_path, '.mindflow', 'tags.json'), 'r') as f:
        tags = json.load(f)
    
    return tags['data'][get_hash(file_path)]['tags']

def list_all_tags(root_path: str) -> list:
    """
    List all the tags extracted from the Markdown files.
    
    :param root_path: The root directory containing the Markdown files.
    :return: A list of all the extracted tags.
    """
    with open(os.path.join(root_path, '.mindflow', 'tags.json'), 'r') as f:
        tags = json.load(f)
    
    return tags['tags']