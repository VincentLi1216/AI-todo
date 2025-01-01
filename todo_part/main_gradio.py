import gradio as gr
import random
import time
from chat_agent_class import TodoChatAgent
from gradio import ChatMessage

todo_agent = TodoChatAgent()

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
    initial_message = [{"role": "assistant", "content": welcome_messages}]
    chatbot = gr.Chatbot(value=initial_message, type="messages", height=900)
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
                elif tool_key == "create_project_from_meeting":
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