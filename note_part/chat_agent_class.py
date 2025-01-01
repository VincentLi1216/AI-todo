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
import datetime

from util_tags import get_file_name_by_tag
from util_create_rag import search_documents, load_vector_store

import re, json

from pydantic import BaseModel, Field

class GetNotesByTagsInput(BaseModel):
    description: str = Field(..., description="The description of the tags to search for.")

class GetContentByQueryInput(BaseModel):
    query: str = Field(..., description="The query to search for.")


class NoteChatAgent:
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

    def get_current_time(self, *args, **kwargs):
        now = datetime.datetime.now()
        return now.strftime("%I:%M %p")

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
                tool_result = {'info': f'Retrieve from "{used_tool[1]['sources']}"'}
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
    agent = NoteChatAgent(root_path="/Users/USER/Desktop/Side_project/MindFlow-AI/note_part/data/TestingNote")
    while True:
        # user_input = input("User: ")
        # user_input = "Can you give me some notes that related to survey of progress and challenges in large language models?"
        user_input = "What is the progress of large language models?"
        if user_input.lower() == "exit":
            break
        agent.chat(user_input)
        break