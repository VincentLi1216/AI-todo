from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_openai import ChatOpenAI

import things

# Load environment variables from .env
load_dotenv()

# Create a ChatOpenAI model
model = ChatOpenAI(model="gpt-4o")

# Define prompt templates (no need for separate Runnable chains)
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a task management assistant specialized in analyzing and summarizing to-do lists provided in JSON format. 
            Your role is to review the provided to-do list, {todo_list}, and generate a concise summary of all tasks. 
            Categorize the tasks based on attributes such as priority, deadline, or category, 
            and suggest any relevant insights or recommendations, such as identifying urgent tasks, approaching deadlines, 
            or potential overlaps. Your response should be clear, structured, and professional, 
            offering both a high-level overview and actionable suggestions where applicable. 
            Use bullet points or organized sections in your response to enhance clarity. Please use Traditional Chinese for the response.""",
        ),
        ("human", "Summarize the todos for me."),
    ]
)

# Create the combined chain using LangChain Expression Language (LCEL)
chain = prompt_template | model | StrOutputParser()
# chain = prompt_template | model

# Run the chain
result = chain.invoke({"todo_list": str(things.today())})

# Output
print(result)
