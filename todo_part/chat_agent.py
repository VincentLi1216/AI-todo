from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

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

# Define Tools
def get_current_time(*args, **kwargs):
    """Returns the current time in H:MM AM/PM format."""
    import datetime

    now = datetime.datetime.now()
    return now.strftime("%I:%M %p")

# List of tools available to the agent
tools = [
    Tool(
        name="Time",
        func=get_current_time,
        description="Useful for when you need to know the current time.",
    ),
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
# Load the correct JSON Chat Prompt from the hub
# https://smith.langchain.com/hub/hwchase17/structured-chat-agent
prompt = ChatPromptTemplate.from_messages([
    ("system", '''
    You are an AI assistant for managing tasks. Respond to the human as helpfully and accurately as possible. Please respond to the user's questions in the language they used to ask. You have access to the following tools:

{tools}

Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).
Valid "action" values: "Final Answer" or {tool_names}
Provide only ONE action per $JSON_BLOB, as shown:

```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```

Follow this format:

Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{{
  "action": "Final Answer",
  "action_input": "Final response to human"
}}
```

Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation.

When you print every todo item, please add a link to it. 
For example:
'uuid': 'Nkuu5DQWS9d6VkMpt5AaAU', 'type': 'to-do', 'title': 'foo_todo_item' -> [foo_todo_item](things:///show?id=$UUID)
$UUID should be replaced with the actual uuid of the todo item.

Begin!'''
),
     MessagesPlaceholder("chat_history"),
     ("human", '''
{input}

{agent_scratchpad}
 (reminder to respond in a JSON blob no matter what)
''')
])


chat_history = []

# Initialize a ChatOpenAI model
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Create a structured Chat Agent with Conversation Buffer Memory
# ConversationBufferMemory stores the conversation history, allowing the agent to maintain context across interactions
memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True)

# create_structured_chat_agent initializes a chat agent designed to interact using a structured prompt and tools
# It combines the language model (llm), tools, and prompt to create an interactive agent
agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)

# AgentExecutor is responsible for managing the interaction between the user input, the agent, and the tools
# It also handles memory to ensure context is maintained throughout the conversation
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    memory=memory,  # Use the conversation memory to maintain context
    handle_parsing_errors=True,  # Handle any parsing errors gracefully
)

# Initial system message to set the context for the chat
# SystemMessage is used to define a message from the system to the agent, setting initial instructions or context
# initial_message = '''You are a task management assistant specialized in analyzing and summarizing to-do lists.
#       You have access to the following tools: all_todos, today_todos'''
# memory.chat_memory.add_message(SystemMessage(content=initial_message))

# Chat Loop to interact with the user


def chat_with_agent(user_input):

    # Invoke the agent with the user input and the current chat history
    response = agent_executor.invoke({"input": user_input})
    print("Bot:", response["output"])
    # Add the user's message to the conversation memory
    memory.chat_memory.add_message(HumanMessage(content=user_input))

    # Add the agent's response to the conversation memory
    memory.chat_memory.add_message(AIMessage(content=response["output"]))



if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break


        chat_with_agent(user_input)