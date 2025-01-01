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

import re, json, time

from pydantic import BaseModel, Field

from util_update_db import create_things_todo, create_things_project
from util_read_db import get_things_projects_names


class CreateTodoInput(BaseModel):
    title: str = Field(title="The title of the todo item")
    notes: str = Field(title="The notes for the todo item")
    project_title: str = Field(
        title=f"The title of the project, choose from {get_things_projects_names()}, if there's no suitable project, input ''"
    )


class CreateProjectInput(BaseModel):
    title: str = Field(title="The title of the project")
    notes: str = Field(title="The notes for the project")
    todos: str = Field(
        title="(Optional) The todos for the project, separate them with comma without space, e.g. 'todo1,todo2,todo3'"
    )


class EmptyInput(BaseModel):
    """空輸入模型，用於無需參數的工具"""

    pass


class TodoChatAgent:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Define tools
        self.tools = [
            StructuredTool(
                name="Time",
                func=self.get_current_time,
                description="Useful for when you need to know the current time. There's no input required.",
                args_schema=EmptyInput,
            ),
            StructuredTool(
                name="all_todos",
                func=self.get_todos,
                description="Useful for when you need to know all todos. There's no input required.",
                args_schema=EmptyInput,
            ),
            StructuredTool(
                name="today_todos",
                func=self.get_today_todos,
                description="Useful for when you need to know today's todos. There's no input required.",
                args_schema=EmptyInput,
            ),
            StructuredTool(
                name="create_todo",
                func=self.create_todo,
                description="""Useful for when you need to create a new todo item. """,
                args_schema=CreateTodoInput,
            ),
            StructuredTool(
                name="create_project",
                func=self.create_project,
                description="""Useful for when you need to create a new project. """,
                args_schema=CreateProjectInput,
            ),
        ]

        # Load the chat prompt template
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
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

Begin!""",
                ),
                MessagesPlaceholder("chat_history"),
                (
                    "human",
                    """
{input}

{agent_scratchpad}
 (reminder to respond in a JSON blob no matter what)
""",
                ),
            ]
        )

        # Initialize language model and memory
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

        # Create the chat agent and executor
        self.agent = create_structured_chat_agent(
            llm=self.llm, tools=self.tools, prompt=self.prompt
        )
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

    def get_todos(self, *args, **kwargs):
        return str(things.todos())

    def get_today_todos(self, *args, **kwargs):
        return str(things.today())

    def get_current_time(self, *args, **kwargs):
        now = datetime.datetime.now()
        return now.strftime("%I:%M %p")

    def create_todo(
        self, title: str, notes: str, project_title: str, show_quick_entry: bool = True, sleep_time: float = 3
    ):
        # 使用 Pydantic 模型進行驗證
        print(f"Title: {title}")
        print(f"Notes: {notes}")
        print(f"Project Title: {project_title}")
        # 在這裡添加處理邏輯，例如與 Things API 交互
        create_things_todo(
            title=title,
            notes=(
                f"Generated by 🛸Mindflow.ai\n{notes}"
                if notes == ""
                else f"{notes}\n\nGenerated by 🛸Mindflow.ai"
            ),
            list_name=project_title,
            show_quick_entry=show_quick_entry,
            tags="🛸AI",
        )
        time.sleep(sleep_time)
        return f"""New Todo Item Created: "{title}", if you receive this message, the todo item has been created successfully. Please don't call it again with the same title."""

    def create_project(self, title: str, notes: str, todos: str = ""):
        # 使用 Pydantic 模型進行驗證
        print(f"Title: {title}")
        print(f"Notes: {notes}")
        # 在這裡添加處理邏輯，例如與 Things API 交互
        create_things_project(
            title=title,
            notes=(
                f"Generated by 🛸Mindflow.ai\n{notes}"
                if notes == ""
                else f"{notes}\n\nGenerated by 🛸Mindflow.ai"
            ),
            tags="🛸AI",
            reveal=True,
        )

        if todos != "":
            todos = todos.split(",")
            for todo in todos:
                self.create_todo(
                    title=todo, project_title=title, notes="", show_quick_entry=False, sleep_time=1.5
                )
            
        time.sleep(3)
        return f'New Project Created: "{title}"'

    def chat(self, user_input):
        # Invoke the agent with the user input
        response = self.agent_executor.invoke({"input": user_input})
        print("Bot:", response["output"])

        intermediate_steps = response["intermediate_steps"]
        used_tools = {}

        for used_tool in intermediate_steps:

            print(used_tool[0].__dict__["tool"])

            # 使用正則提取
            matched_tool = used_tool[0].__dict__["tool"]
            print("Extracted tool:", matched_tool)
            if matched_tool == "Time":
                tool_result = f'Returns: "{used_tool[1]}"'
            elif matched_tool == "all_todos":
                tool_result = (
                    f'Returns "{len(ast.literal_eval(used_tool[1]))}" Todos Items'
                )
            elif matched_tool == "today_todos":
                tool_result = (
                    f'Returns "{len(ast.literal_eval(used_tool[1]))}" Todos Items'
                )
            elif matched_tool == "create_todo":
                tool_result = f"{used_tool[1]}"
            elif matched_tool == "create_project":
                tool_result = f"{used_tool[1]}"
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
