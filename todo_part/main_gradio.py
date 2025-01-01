import gradio as gr
import random
import time
from chat_agent_class import TodoChatAgent
from gradio import ChatMessage

todo_agent = TodoChatAgent()

with gr.Blocks() as demo:

    chatbot = gr.Chatbot(type="messages", height=900)
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    def respond(message, chat_history):
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
        respond = f'<div style="width: 900px;"> {respond} </div>'
        chat_history.append({"role": "assistant", "content": gr.HTML(respond)})
        # foo_respond = "[google](https://www.google.com)\n[Things](things:///show?id=Nkuu5DQWS9d6VkMpt5AaAU)\n- one\n- two\n- three\n# this is the title"
        # foo_respond = '<a href="things:///show?id=Nkuu5DQWS9d6VkMpt5AaAU" style="color:blue; text-decoration:underline;" target="_blank">things:///show?id=Nkuu5DQWS9d6VkMpt5AaAU</a>'
        # foo_respond = '<a href="https://google.com" style="color:blue; text-decoration:underline;" target="_blank">things:///show?id=Nkuu5DQWS9d6VkMpt5AaAU</a>'
        # foo_respond = gr.HTML("<h1>12345678678678</h1><a href='things:///show?id=Nkuu5DQWS9d6VkMpt5AaAU'>Gradio</a>")
        # chat_history.append({"role": "assistant", "content": foo_respond})
        return "", chat_history
    
    def clear_memory():
        todo_agent.clear_memory()
        return "Memory cleared."

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear.click(clear_memory)

if __name__ == "__main__":
    demo.launch(debug=True)