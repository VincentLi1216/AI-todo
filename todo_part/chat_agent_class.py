from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import things
import datetime

class TodoChatAgent:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Define tools
        self.tools = [
            Tool(
                name="Time",
                func=self.get_current_time,
                description="Useful for when you need to know the current time.",
            ),
            Tool(
                name="all_todos",
                func=self.get_todos,
                description="Useful for when you need to know all todos.",
            ),
            Tool(
                name="today_todos",
                func=self.get_today_todos,
                description="Useful for when you need to know today's todos.",
            )
        ]

        # Load the chat prompt template
        self.prompt = ChatPromptTemplate.from_messages([
    ("system", '''
    Respond to the human as helpfully and accurately as possible. You have access to the following tools:

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
'uuid': 'Nkuu5DQWS9d6VkMpt5AaAU', 'type': 'to-do', 'title': 'foo_todo_item' -> <a href='things:///show?id=$UUID>foo_todo_item</a>
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

        # Initialize language model and memory
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Create the chat agent and executor
        self.agent = create_structured_chat_agent(llm=self.llm, tools=self.tools, prompt=self.prompt)
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True,
        )

    def get_todos(self, *args, **kwargs):
        return str(things.todos())

    def get_today_todos(self, *args, **kwargs):
        return str(things.today())

    def get_current_time(self, *args, **kwargs):
        now = datetime.datetime.now()
        return now.strftime("%I:%M %p")

    def chat(self, user_input):
        # Invoke the agent with the user input
        response = self.agent_executor.invoke({"input": user_input})
        print("Bot:", response["output"])

        # Add messages to memory
        self.memory.chat_memory.add_message(HumanMessage(content=user_input))
        self.memory.chat_memory.add_message(AIMessage(content=response["output"]))
        return response["output"]
    
    # clear memory function
    def clear_memory(self):
        self.memory.chat_memory.clear()

if __name__ == "__main__":
    agent = TodoChatAgent()
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break
        agent.chat(user_input)
