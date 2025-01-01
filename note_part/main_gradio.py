import gradio as gr
import random
import time
from chat_agent_class import NoteChatAgent
from gradio import ChatMessage

from common import list_md_files, get_summary, get_tags, list_all_tags
from util_sumarization import summarize_file
from util_tags import tag as tag_file

todo_agent = NoteChatAgent(root_path="/Users/USER/Desktop/Side_project/MindFlow-AI/note_part/data/TestingNote")

files = []
for file in list_md_files(todo_agent.root_path):
    files.append(file['relative_path'])
    
tags = list_all_tags(todo_agent.root_path)

with gr.Blocks() as demo:
    selected_files = gr.State([])
    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot(type="messages", height=600)
            msg = gr.Textbox()
            clear = gr.ClearButton([msg, chatbot])

            def respond(message, chat_history, files_dropdown):
                respond, used_tools = todo_agent.chat(message)
                chat_history.append({"role": "user", "content": message})
                respond = respond.replace("\n", "<br>")
                if len(used_tools.keys())>0:
                    for tool_key in used_tools.keys():
                        if tool_key == "Get_related_notes_by_tags":
                            files_dropdown = used_tools[tool_key]['sources']
                            chat_history.append(
                                ChatMessage(role="assistant",
                                content=f"{used_tools[tool_key]['info']}",
                                metadata={"title": f'⏱️ Used tool "{tool_key}"'})
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
            root_path_textbox = gr.Textbox(todo_agent.root_path, label="Root Path")
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
            with gr.Accordion("Overview"):
                def update_overview(selected_files):
                    return get_summary(todo_agent.root_path, selected_files), get_tags(todo_agent.root_path, selected_files)
                def generate_summary(selected_files):
                    return summarize_file(todo_agent.root_path, selected_files)
                def generate_tags(selected_files):
                    return tag_file(todo_agent.root_path, selected_files, rewrite=True)
                    
                summary_dropdown = gr.Dropdown(files, value=[], multiselect=False, interactive=True, label="Select a file to overview")
                summary_textfield = gr.Textbox("", label="Summary")
                tags_filed = gr.Dropdown(tags, value=[], multiselect=True, interactive=False, label="Tags")
                summary_dropdown.change(update_overview, summary_dropdown, [summary_textfield, tags_filed])
                with gr.Row():
                    summary_button = gr.Button("Get Summary")
                    tags_button = gr.Button("Get Tags")
                    summary_button.click(generate_summary, summary_dropdown, summary_textfield)
                    tags_button.click(generate_tags, summary_dropdown, tags_filed)
    
    msg.submit(respond, [msg, chatbot, files_dropdown], [msg, chatbot, selected_files])
    clear.click(clear_memory)

if __name__ == "__main__":
    demo.launch(debug=True)