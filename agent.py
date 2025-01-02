from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import Tool, StructuredTool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import things
import ast
import time
import datetime

from note_part.util_tags import get_file_name_by_tag
from note_part.util_create_rag import search_documents, load_vector_store

from todo_part.util_update_db import create_things_todo, create_things_project
from todo_part.util_read_db import get_things_projects_names

import re, json, os

from pydantic import BaseModel, Field

class GetNotesByTagsInput(BaseModel):
    description: str = Field(..., description="The description of the tags to search for.")

class GetContentByQueryInput(BaseModel):
    query: str = Field(..., description="The query to search for.")
    
    
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


class ChatAgent:
    def __init__(self, root_path):
        # Load environment variables
        load_dotenv()
        
        self.root_path = root_path
        self.selected_files = []

        # Define tools
        self.tools = [
            Tool(
                name="Time",
                func=self.get_current_time,
                description="Useful for when you need to know the current time.",
            ),
            StructuredTool(
                name="Get_related_notes_by_tags",
                func=self.get_notes_by_tags,
                description="Useful for when user ask some note files that related to some topics.",
                args_schema=GetNotesByTagsInput
            ),
            StructuredTool(
                name="Retrive_related_content",
                func=self.get_related_content,
                description="Useful for when user ask the related content based on the query.",
                args_schema=GetContentByQueryInput
            ),
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
            StructuredTool(
                name="create_project_from_meeting",
                func=self.create_project_from_meeting,
                description="""Useful for when you need to create a new project from a meeting record. """,
                args_schema=EmptyInput,
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
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
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

    def get_notes_by_tags(self, description: str):
        file_names = get_file_name_by_tag(self.root_path, description)
        return file_names
    
    def get_related_content(self, query: str):
        if len(self.selected_files) == 0:
            return {'contents': "Please select the files first.", 'sources': []}
        vector_store = load_vector_store(self.embeddings, self.root_path)
        results = search_documents(vector_store, query, target=self.selected_files)
        contents = ""
        sources = []
        for result in results:
            if result.metadata["source"] not in sources:
                sources.append(result.metadata["source"])
            contents += str(result.metadata)
            contents += "\n"
            contents += result.page_content
            contents += ("-" * 100)
            contents += "\n"
            
        return {'contents': contents, 'sources': sources}
    
    def get_todos(self, *args, **kwargs):
        return str(things.todos())

    def get_today_todos(self, *args, **kwargs):
        return str(things.today())

    def get_current_time(self, *args, **kwargs):
        now = datetime.datetime.now()
        return now.strftime("%I:%M %p")

    def create_todo(
        self, title: str, notes: str, project_title: str, show_quick_entry: bool = True, sleep_time: float = 3, reveal: bool = False
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
    
    def create_project_from_meeting(self, *args, **kwargs):
        project_title = "第一次行銷策略討論-會議記錄"

        self.create_project(title=project_title, notes="在 2024 年 12 月 22 日的會議中，討論了新型科技產品 \"智感耳機 SenseHear\" 的開發進度。SenseHear 結合 AI 及多功能感測技術，旨在提供智慧音頻體驗。會議回顧了上次的進展，包括市場調研初稿和競品分析初步結果。設計師提出了交互設計模型，計劃在年底前完成第三次迭代草圖。技術上，已整合感測模組與降噪技術，目標在 2025 年 2 月 10 日完成原型機技術驗證。行銷策略聚焦健康生活，品牌形象將於 2025 年 2 月中推出首波宣傳。下一步包括完成原型設計、焦點小組調查及專利申請。團隊確認每兩周檢討進度，以確保 SenseHear 的如期推出和成功。")

        # open json to dict
        with open("note_part/todo_item_list.template.json", "r") as f:
            meeting_todo_list = json.load(f)

        for todo in meeting_todo_list:
            self.create_todo(
                title=todo["title"], project_title=project_title, notes=todo["task"], show_quick_entry=False, sleep_time=1, reveal=True
            )

        return f"""New Project Created: "{project_title}" and todos created from the meeting record"""

    def chat(self, user_input):
        # Invoke the agent with the user input
        response = self.agent_executor.invoke({"input": user_input})
        print("Bot:", response["output"])

        intermediate_steps = response["intermediate_steps"]
        used_tools = {}

        for used_tool in intermediate_steps:
            # print("Used tool:", used_tool)
            matched_tool = used_tool[0].__dict__["tool"]
            print("Extracted tool:", matched_tool)
            if matched_tool == "Time":
                tool_result = {'info': f'Returns: "{used_tool[1]}"'}
            elif matched_tool == "Get_related_notes_by_tags":
                tool_result = {'info': f'Returns "{used_tool[1]}', 'sources': used_tool[1]}
            elif matched_tool == "Retrive_related_content":
                tool_result = {'info': f'Retrieve from "{used_tool[1]["sources"]}"'}
            elif matched_tool == "Time":
                tool_result = {'info': f'Returns: "{used_tool[1]}"'}
            elif matched_tool == "all_todos":
                tool_result = {'info': f'Returns "{len(ast.literal_eval(used_tool[1]))}" Todos Items'}
            elif matched_tool == "today_todos":
                tool_result = {'info': f'Returns "{len(ast.literal_eval(used_tool[1]))}" Todos Items'}
            elif matched_tool == "create_todo":
                tool_result = {'info': f"{used_tool[1]}"}
            elif matched_tool == "create_project":
                tool_result = {'info': f"{used_tool[1]}"}
            elif matched_tool == "create_project_from_meeting":
                tool_result = f"{used_tool[1]}"
            used_tools[matched_tool] = tool_result

        print(response)
        print(used_tools)

        # Add messages to memory
        self.memory.chat_memory.add_message(HumanMessage(content=user_input))
        self.memory.chat_memory.add_message(AIMessage(content=response["output"]))
        return str(response["output"]), used_tools
    
    # clear memory function
    def clear_memory(self):
        self.memory.chat_memory.clear()

if __name__ == "__main__":
    load_dotenv()
    root_path = os.getenv("ROOT_PATH")
    agent = ChatAgent(root_path=root_path)
    while True:
        # user_input = input("User: ")
        # user_input = "Can you give me some notes that related to survey of progress and challenges in large language models?"
        user_input = "What is the progress of large language models?"
        if user_input.lower() == "exit":
            break
        agent.chat(user_input)
        break