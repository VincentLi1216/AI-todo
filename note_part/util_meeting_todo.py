import os
from typing import List, Union, Literal
from llm import OpenAILLM
from pydantic import BaseModel, Field
from datetime import date

llm = OpenAILLM()

template = """Extract all to-do items from the provided meeting notes, ensuring each item includes the expected completion time and a detailed description of the task. Optionally include any additional relevant details such as location or the responsible person.

# Steps

1. Carefully read through the provided meeting notes to identify tasks or action items.
2. For each task or action item:
   - Determine the expected completion time.
   - Provide a detailed description of the task.
   - Include any additional information like the location or assigned person when possible.
3. Ensure that each to-do item contains comprehensive details about the task and when it should be done.
4. If a specific completion time, assignees is not mentioned, use contextual information to estimate it when feasible.
5. Compile these details into a structured list with consistency in the format of each to-do item.

# Output Format

Provide the to-do items in a clear, consistent list format, where each item contains:
- Expected completion time
- Task description
- Additional details (optional)

# Notes

- Ensure clarity and completeness in the task descriptions to prevent misinterpretation.
- Use context to fill out any unspecified fields wherever possible.
- Maintain consistency in the structure of each to-do item to ensure clarity and ease of understanding.

# Here are the meeting notes:
{document}
"""

class TodoItem(BaseModel):
    title: str = Field(description="The title or name of the task.")
    task: str = Field(description="The detailed description of the task.")
    completion_time: date = Field(description="The expected completion time for the task.")
    priority: Literal["high", "medium", "low"] = Field(description="The priority level of the task.")
    place: Union[str, None] = Field(description="The location or place associated with the task.")
    person: Union[str, None] = Field(description="The responsible person for the task. Seperate multiple persons with ', '")

class TodoList(BaseModel):
    items: List[TodoItem] = Field(description="The list of extracted to-do items.")


llm.build(template=template, schema=TodoList)


def extract_todos(file_path: str) -> List[TodoItem]:
    """
    Extract all to-do items from the provided meeting notes.
    
    :param file_path: The file path of the meeting notes.
    :return: A list of extracted to-do items.
    """
    content = open(file_path, 'r').read()
    response = llm.invoke({"document": content})
    
    return response.items


if __name__ == "__main__":
    root_path = "/Users/USER/Desktop/Side_project/MindFlow-AI/note_part/data/TestingNote"
    file_path = "Meeting/第一次行銷策略討論-會議記錄.md"
    
    todos = extract_todos(os.path.join(root_path, file_path))
    for todo in todos:
        print(todo.__dict__)