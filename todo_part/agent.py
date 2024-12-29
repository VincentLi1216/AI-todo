from dotenv import load_dotenv
from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
)
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

import things

# Load environment variables from .env file
load_dotenv()

def get_todos(*args, **kwargs):
    """
    Get all todos from Things.
    
    :return: A list of todos.
    """
    return str(things.todos())


def get_today_todos(*args, **kwargs):
    """
    Get today's todos from Things.
    
    :return: A list of today's todos.
    """
    return str(things.today())

# List of tools available to the agent
tools = [
    Tool(
        name="all_todos",
        func=get_todos,
        description="Useful for when you need to know all todos.",
    ),
    Tool(
        name="today_todos",
        func=get_today_todos,
        description="Useful for when you need to know today's todos.",
    )
]

# Pull the prompt template from the hub
prompt = ChatPromptTemplate.from_messages(
    [("system", '''You are a task management assistant specialized in analyzing and summarizing to-do lists.
      You have access to the following tools: {tools}
      Use the following format to process and organize the to-do lists:
      Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of {tool_names}
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final summary or response to the input question, when you print every todo item, please add a link to it. 
      ex. 'uuid': 'Nkuu5DQWS9d6VkMpt5AaAU', 'type': 'to-do', 'title': 'foo_todo_item' -> [foo_todo_item](things:///show?id=$UUID)
      $UUID should be replaced with the actual uuid of the todo item.
      
      Begin!

    Question: {input}
    Thought: {agent_scratchpad}
'''
    )]
)

# Initialize a ChatOpenAI model
llm = ChatOpenAI(
    model="gpt-4o", temperature=0
)

# Create the ReAct agent using the create_react_agent function
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
    stop_sequence=True,
)

# Create an agent executor from the agent and tools
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# Run the agent with a test query
response = agent_executor.invoke({"input": "what are all today's todos?"})

# Print the response from the agent
print("response:", response["output"])
