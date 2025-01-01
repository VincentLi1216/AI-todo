import gradio as gr
import random
import time
from agent import ChatAgent
from gradio import ChatMessage

from note_part.common import list_md_files, get_summary, get_tags, list_all_tags
from note_part.util_sumarization import summarize_file
from note_part.util_tags import tag as tag_file

todo_agent = ChatAgent(root_path="/Users/USER/Desktop/Side_project/MindFlow-AI/note_part/data/TestingNote")

files = []
for file in list_md_files(todo_agent.root_path):
    files.append(file['relative_path'])
    
tags = list_all_tags(todo_agent.root_path)

welcome_messages = '''
嗨！我是你的智能待辦事項助理，專為提升效率和簡化生活而設計！🎉

以下是我可以幫助你的方式：
1️⃣ 目標分解

提供你的目標，我會自動將它分解為可執行的任務，幫助你更輕鬆地完成計劃。
2️⃣ 待辦事項查詢

隨時查詢你的待辦清單內容，包括未完成的任務、到期時間及優先級，讓你掌握所有細節。
3️⃣ 自然語言互動

用簡單的對話方式管理清單，例如新增、刪除或編輯任務，我會隨時為你處理！
試試以下指令來開始吧：

「我要計劃一場生日派對」
「告訴我明天的待辦事項」
「幫我新增一個重要的任務，明天上午提醒我！」

準備好了嗎？輸入你的第一個需求，我們一起開始吧！ 🚀
'''

with gr.Blocks() as demo:
    root_path_textbox = gr.Textbox(todo_agent.root_path, label="Root Path")
    with gr.Tab("Chat"):
        selected_files = gr.State([])
        with gr.Row():
            with gr.Column():
                initial_message = [{"role": "assistant", "content": welcome_messages}]
                chatbot = gr.Chatbot(value=initial_message, type="messages", height=600)
                msg = gr.Textbox()
                clear = gr.ClearButton([msg, chatbot])

                def respond(message, chat_history, files_dropdown):
                    respond, used_tools = todo_agent.chat(message)
                    chat_history.append({"role": "user", "content": message})
                    respond = respond.replace("\n", "<br>")
                    if len(used_tools.keys())>0:
                        for tool_key in used_tools.keys():
                            if tool_key == "Time":
                                chat_history.append(
                                    ChatMessage(role="assistant",
                                    content=f"{used_tools[tool_key]}",
                                    metadata={"title": f'⏱️ Used tool "{tool_key}"'})
                                )
                            elif tool_key == "all_todos":
                                chat_history.append(
                                    ChatMessage(role="assistant",
                                    content=f"{used_tools[tool_key]}",
                                    metadata={"title": f'🤖 Used tool "{tool_key}"'})
                                )
                            elif tool_key == "today_todos":
                                chat_history.append(
                                    ChatMessage(role="assistant",
                                    content=f"{used_tools[tool_key]}",
                                    metadata={"title": f'🤖 Used tool "{tool_key}"'})
                                )
                            elif tool_key == "create_todo":
                                chat_history.append(
                                    ChatMessage(role="assistant",
                                    content=f"{used_tools[tool_key]}",
                                    metadata={"title": f'🎯 Used tool "{tool_key}"'}))
                            elif tool_key == "create_project":
                                chat_history.append(
                                    ChatMessage(role="assistant",
                                    content=f"{used_tools[tool_key]}",
                                    metadata={"title": f'🎯 Used tool "{tool_key}"'}))
                                
                            elif tool_key == "Get_related_notes_by_tags":
                                files_dropdown = used_tools[tool_key]['sources']
                                chat_history.append(
                                    ChatMessage(role="assistant",
                                    content=f"{used_tools[tool_key]['info']}",
                                    metadata={"title": f'🗒️ Used tool "{tool_key}"'})
                                )
                            else:
                                chat_history.append(
                                    ChatMessage(role="assistant",
                                    content=f"{used_tools[tool_key]['info']}",
                                    metadata={"title": f'🗒️ Used tool "{tool_key}"'})
                                )
                    respond = f'<div style="width: 100%;"> {respond} </div>'
                    chat_history.append({"role": "assistant", "content": gr.HTML(respond)})
                    return "", chat_history, files_dropdown
            
                def clear_memory():
                    todo_agent.clear_memory()
                    return "Memory cleared."
                
            with gr.Column():
                with gr.Accordion("Selected Files"):
                    def select_all(selected_files):
                        selected_files = files.copy()
                        return selected_files
                    def update_files(selected_files):
                        update_agent_files(selected_files)
                        return selected_files
                    def update_agent_files(selected_files):
                        todo_agent.selected_files = selected_files
                    files_dropdown = gr.Dropdown(files, value=selected_files, multiselect=True, interactive=True)
                    files_dropdown.change(update_agent_files, files_dropdown)
                    select_all_button = gr.Button("Select All")
                    select_all_button.click(select_all, selected_files, selected_files)
                    selected_files.change(update_files, selected_files, files_dropdown)
                    
        msg.submit(respond, [msg, chatbot, files_dropdown], [msg, chatbot, selected_files])
        clear.click(clear_memory)
    
    with gr.Tab("Note"):
        with gr.Row():
            with gr.Accordion("Overview"):
                def update_overview(selected_files):
                    return get_summary(todo_agent.root_path, selected_files), get_tags(todo_agent.root_path, selected_files)
                def generate_summary(selected_files):
                    return summarize_file(todo_agent.root_path, selected_files)
                def generate_tags(selected_files):
                    new_tags = tag_file(todo_agent.root_path, selected_files, rewrite=True)
                    return gr.Dropdown(list_all_tags(todo_agent.root_path), value=new_tags, multiselect=True, interactive=False, label="Tags")
                    
                summary_dropdown = gr.Dropdown(files, value=[], multiselect=False, interactive=True, label="Select a file to overview")
                summary_textfield = gr.Textbox("", label="Summary")
                tags_filed = gr.Dropdown(tags, value=[], multiselect=True, interactive=False, label="Tags")
                summary_dropdown.change(update_overview, summary_dropdown, [summary_textfield, tags_filed])
                with gr.Row():
                    summary_button = gr.Button("Get Summary")
                    tags_button = gr.Button("Get Tags")
                    summary_button.click(generate_summary, summary_dropdown, summary_textfield)
                    tags_button.click(generate_tags, summary_dropdown, tags_filed)

if __name__ == "__main__":
    demo.launch(debug=True)