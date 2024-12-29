import gradio as gr
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
import things
import datetime

# Load environment variables
load_dotenv()

def get_todos(*args, **kwargs):
    return str(things.todos())

def get_today_todos(*args, **kwargs):
    return str(things.today())

def get_current_time(*args, **kwargs):
    now = datetime.datetime.now()
    return now.strftime("%I:%M %p")

# Define Tools
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

# Load the chat prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", '''Respond to the human as helpfully and accurately as possible. You have access to the following tools:

{tools}

Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).
Valid "action" values: "Final Answer" or {tool_names}
Provide only ONE action per $JSON_BLOB, as shown:

```
{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}
```

Begin!'''),
    MessagesPlaceholder("chat_history"),
    ("human", '''{input}

{agent_scratchpad}''')
])

# Initialize the language model and memory
llm = ChatOpenAI(model="gpt-4", temperature=0)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Create the chat agent
agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    memory=memory,
    handle_parsing_errors=True,
)

def chat_with_agent(user_input, chat_history):
    memory.chat_memory.messages = chat_history
    response = agent_executor.invoke({"input": user_input})
    chat_history.append(HumanMessage(content=user_input))
    chat_history.append(AIMessage(content=response["output"]))
    return response["output"], chat_history

# Gradio interface
def launch_gradio_interface():
    pass

with gr.Blocks() as demo:
    chat_history_state = gr.State([])

    with gr.Row():
        gr.Markdown("## TODO Chat Agent")

    with gr.Row():
        chatbox = gr.Chatbot()

    with gr.Row():
        user_input = gr.Textbox(placeholder="Type your message here...")
        send_button = gr.Button("Send")

    def user_interaction(user_input, chat_history):
        response, updated_history = chat_with_agent(user_input, chat_history)
        return updated_history, updated_history

    send_button.click(user_interaction, inputs=[user_input, chat_history_state], outputs=[chatbox, chat_history_state])

demo.launch()

if __name__ == "__main__":
    # launch_gradio_interface()
    pass
