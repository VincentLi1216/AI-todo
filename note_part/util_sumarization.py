import os
from llm import OpenAILLM
from langchain_core.pydantic_v1 import BaseModel, Field

llm = OpenAILLM()

template = """Generate a concise summary based on the provided document content. The summary should be limited to a single paragraph and must be written in the same language as the original document.

# Steps

1. Read and understand the full content of the document provided.
2. Identify the main points, arguments, or essential information in the document.
3. Synthesize these key points into a single coherent paragraph, ensuring the information flows logically.
4. Maintain the language used in the original document for consistency.

# Output Format

- A single paragraph summarizing the document.
- Maintain the same language as the original document for the summary. 

# Notes

- Focus on clarity, ensuring that the most relevant information is captured succinctly.
- Avoid adding your own opinions or interpretations beyond what is presented in the document.

# Here is the document content:

{document}
"""

class SummarizeResponse(BaseModel):
    text: str = Field(description="The summarized text.")
    
llm.build(template=template, schema=SummarizeResponse)


def summarize(root_path: str, file_path: str) -> str:
    """
    Generate a concise summary based on the provided document content.
    
    :param root_path: The root path of the note folder.
    :param file_path: The file path of the note file.
    :return: The summarized text.
    """
    content =  f"""
# {file_path.split('/')[-1].replace('.md', '')}
---
{open(os.path.join(root_path, file_path), 'r').read()}
"""
    response = llm.invoke({"document": content})
    
    return response.text


if __name__ == "__main__":
    root_path = "/Users/USER/Desktop/Side_project/MindFlow-AI/note_part/data/TestingNote"
    file_path = "paper/Large Language Model based Multi-Agents- A Survey of Progress and Challenges.md"
    
    print(summarize(root_path, file_path))