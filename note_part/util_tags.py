import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(current_dir)

import os
import re
import json
from transformers import pipeline
from llm import OpenAILLM
from pydantic import BaseModel, Field
import hashlib

from common import list_md_files, get_hash

llm = OpenAILLM("gpt-4o-mini")

hypothesis_template = "This text is about {}"
zeroshot_classifier = pipeline("zero-shot-classification", model="MoritzLaurer/deberta-v3-large-zeroshot-v2.0")  # change the model identifier here

template = """Generate 5 to 10 relevant tags for categorizing the provided document content.

- Ensure the tags are specific and accurately reflect the main topics or key concepts discussed in the content.
- Avoid duplicating any existing tags. 
Here are the existing tags: {tags}.
- Use concise terms for each tag, ideally limiting each to no more than 3 words.
- Arrange the generated tags in descending order of relevance, with the most relevant tags listed first.

# Steps

1. Read and analyze the provided document content thoroughly to identify the main topics and key concepts.
2. Based on the analysis, brainstorm potential tags that capture these key ideas.
3. Cross-check each potential tag against the list of existing tags and eliminate duplicates.
4. Rank the potential tags by their relevance to the document content.
5. Select the top 0 to 8 relevant tags.
6. Ensure that each tag is concise, consisting of no more than 3 words.

# Notes

- Focus on specificity and conciseness for the tags.
- Consider the primary and secondary topics, as well as any specialized terms, discussed in the document.

# Document Content
{document}
"""

class RelativeTag(BaseModel):
    tags: list[str] = Field(
        ...,
        description="List of tags generated based on the content of the document.",
    )
    
llm.build(template=template, schema=RelativeTag)

def tag_template_matching(text: str, remove: bool = False) -> tuple[bool, str]:
    pattern = r'(?s)^---\ntags:\n.*?\n---'

    if re.match(pattern, text, re.DOTALL):
        if remove:
            updated_text = re.sub(pattern, '', text, count=1, flags=re.DOTALL)
            return True, updated_text.strip()
        return True, text
    else:
        return False, text


def classify_text(text: str, classes: list) -> dict:
    response = llm.invoke({
        "document": text,
        "tags": classes
    })
    return response.tags


def pick_existing_classes(text: str, classes_verbalized: list, target_score: float = 0.88, limit: int = 6) -> list:
    """
    Pick the classes that are most likely to be present in the text.
    
    :param text: The input text to be classified.
    :param classes: The list of classes to choose from.
    :return: The list of classes most likely to be present in the text.
    """
    if len(classes_verbalized) == 0:
        return []
    output = zeroshot_classifier(text, classes_verbalized, hypothesis_template=hypothesis_template, multi_label=True)
    # print(output)
    result = []
    for i, score in enumerate(output["scores"]):
        if score > target_score:
            result.append(output["labels"][i])
        if len(result) == limit:
            break
            
    return result 


def tag(root_path, file_path, rewrite=False):
    """
    Tag the specified Markdown file with relevant classes based on its content.
    
    :param root_path: The root directory containing the Markdown files.
    :param file_path: The relative path of the Markdown file to be tagged.
    :return: A message indicating the completion of the tagging process.
    """
    if 'tags.json' not in os.listdir(os.path.join(root_path, '.mindflow')):
        print("Creating the tags.json file...")
        tags = {'root': root_path, 'file': [], 'tags': [], 'data': {}}
        with open(os.path.join(root_path, '.mindflow', 'tags.json'), 'w') as f:
            f.write(json.dumps(tags))
    else:
        with open(os.path.join(root_path, '.mindflow', 'tags.json'), 'r') as f:
            tags = json.load(f)
    
    if file_path not in tags['file']:
        tags['file'].append(file_path)
    elif not rewrite:
        return "File already tagged."
    
    content = open(os.path.join(root_path, file_path), 'r').read()
    content = tag_template_matching(content, True)[1]
    
    labels = pick_existing_classes(content, tags['tags'])
    results = classify_text(content, labels)[:10-len(labels)]
    labels = list(set(results + labels))
    
    tag_template = """---\ntags:\n{tags}---"""
    
    string_tags = ""
    for label in labels:
        string_tags += f"  - {label}\n"
    
    content = f"{tag_template.format(tags=string_tags)}\n{content}"

    with open(os.path.join(root_path, file_path), 'w') as f:
        f.write(content)
    
    tags['data'][get_hash(file_path)] = {
        'file': file_path,
        'tags': labels
    }
    
    for label in labels:
        if label not in tags['tags']:
            tags['tags'].append(label)
    
    with open(os.path.join(root_path, '.mindflow', 'tags.json'), 'w') as f:
        f.write(json.dumps(tags))
    
    return labels


def batch_tag(root_path):
    """
    Batch process all the Markdown files in the provided directory and tag each file with relevant classes based on its content.
    
    :param root_path: The root directory containing the Markdown files.
    :return: A message indicating the completion of the tagging process.
    """
    md_files = list_md_files(root_path)
    
    for file_path in md_files:
        print(file_path['relative_path'])
        tag(root_path, file_path['relative_path'], rewrite=True)
        
    return "Batch tagging process completed successfully."


def get_file_name_by_tag(root_path, description):
    """
    Get the list of files that are tagged with the specified tag.
    
    :param root_path: The root directory containing the Markdown files.
    :param tag_name: The name of the tag to search for.
    :return: A list of files tagged with the specified tag.
    """
    with open(os.path.join(root_path, '.mindflow', 'tags.json'), 'r') as f:
        tags = json.load(f)
        
    related_tags = pick_existing_classes(description, tags['tags'], target_score=0.7, limit=100)
    print(related_tags)
    tag_to_files = {}
    for entry in tags['data'].values():
        file_name = entry["file"]
        for tag in entry["tags"]:
            if tag not in tag_to_files:
                tag_to_files[tag] = []
            tag_to_files[tag].append(file_name)
    
    result = []
    for tag in related_tags:
        if tag in tag_to_files:
            result.extend(tag_to_files[tag])
    
    return list(set(result))