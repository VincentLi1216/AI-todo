from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import Tool, StructuredTool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import things
import ast
import datetime

import re, json

from pydantic import BaseModel, Field

class CreateTodoInput(BaseModel):
    title: str = Field(title="The title of the todo item")
    notes: str = Field(title="The notes for the todo item")
    project_title: str = Field(title="The title of the project")



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
            ),
            StructuredTool(
                name="create_todo",
                func=self.create_todo,
                description='''Useful for when you need to create a new todo item.''',
                args_schema=CreateTodoInput
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
            return_intermediate_steps=True
        )

    def get_todos(self, *args, **kwargs):
        return str(things.todos())

    def get_today_todos(self, *args, **kwargs):
        return str(things.today())

    def get_current_time(self, *args, **kwargs):
        now = datetime.datetime.now()
        return now.strftime("%I:%M %p")
    

    def create_todo(self, title: str, notes: str, project_title: str):
        # 使用 Pydantic 模型進行驗證
        print(f"Title: {title}")
        print(f"Notes: {notes}")
        print(f"Project Title: {project_title}")
        # 在這裡添加處理邏輯，例如與 Things API 交互

        return "todo item created"

    def chat(self, user_input):
        # Invoke the agent with the user input
        response = self.agent_executor.invoke({"input": user_input})
        print("Bot:", response["output"])

        intermediate_steps = response["intermediate_steps"]
        used_tools = {}

        for used_tool in intermediate_steps:

            print(used_tool[0].__dict__["tool"])
            def str_to_json(str_data):
                str_data = str_data.replace("'", '"').replace("None", "null")
                try:
                    actual_list = json.loads(str(str_data))
                    print("轉換後的列表:", actual_list)
                    print("類型:", type(actual_list))
                    return actual_list
                except json.JSONDecodeError as e:
                    print("解析失敗:", e)

            # 使用正則提取
            matched_tool = used_tool[0].__dict__["tool"]
            print("Extracted tool:", matched_tool)
            if matched_tool == "Time":
            
                tool_result = f'Returns: "{used_tool[1]}"'
            elif matched_tool == "all_todos":
                
                tool_result = f'Returns "{len(ast.literal_eval(used_tool[1]))}" Todos Items'
            elif matched_tool == "today_todos":
                tool_result = f'Returns "{len(ast.literal_eval(used_tool[1]))}" Todos Items'
            elif matched_tool == "create_todo":
                tool_result = f'Created a new todo item: '
            used_tools[matched_tool] = tool_result
            

        print(response)
        print(used_tools)

        # Add messages to memory
        self.memory.chat_memory.add_message(HumanMessage(content=user_input))
        self.memory.chat_memory.add_message(AIMessage(content=response["output"]))
        return response["output"], used_tools
    
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
