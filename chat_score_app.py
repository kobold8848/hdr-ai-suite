import streamlit as st
from datetime import datetime

st.set_page_config(page_title="对话", page_icon="💬")
st.markdown(
    """
    <style>
    .user-bubble {
        background: #d2f7ff; color: #222; padding:12px 18px;
        border-radius:18px 0 18px 18px; margin:6px 0; text-align:right;
        max-width:60%; float:right; clear:both; font-size:16px;
    }
    .ai-bubble {
        background: #f0f2fa; color: #222; padding:12px 18px;
        border-radius:0 18px 18px 18px; margin:6px 0; text-align:left;
        max-width:60%; float:left; clear:both; font-size:16px;
    }
    .bubble-meta { color: #aaa; font-size:12px; margin-top:2px; }
    .bubble-wrap { width:100%; display:block; overflow:auto; }
    </style>
    """, unsafe_allow_html=True
)

st.title("对话")

# 聊天历史
if "history" not in st.session_state:
    st.session_state["history"] = []

# 用于手动清空输入框的变量
if "clear_input" not in st.session_state:
    st.session_state["clear_input"] = False

# 1. 文件上传控件
uploaded_files = st.file_uploader(
    "拖拽或选择文件(支持 JPG/TIF/RAW 等, 最大200MB)",
    type=["jpg", "jpeg", "png", "tif", "tiff", "dng", "cr2", "cr3", "nef"],
    accept_multiple_files=True,
    key="file_uploader"
)

# 2. 输入框控件（配合“清空输入框”实现）
def input_on_change():
    st.session_state["clear_input"] = False

user_input = st.text_input(
    "输入你的问题...",
    value="" if st.session_state["clear_input"] else st.session_state.get("user_input", ""),
    key="user_input",
    on_change=input_on_change,
)

# 是否可发送
can_send = (uploaded_files and len(uploaded_files) > 0) or (user_input and user_input.strip() != "")

# 3. 发送按钮
send_btn = st.button("发送", disabled=not can_send)

# 4. 处理逻辑
if send_btn:
    msg_time = datetime.now().strftime("%H:%M:%S")
    user_bubbles = []

    # 用户文本
    current_input = user_input.strip()
    if current_input:
        user_bubbles.append({
            "type": "text",
            "content": current_input,
            "timestamp": msg_time
        })

    # 用户上传的文件
    if uploaded_files and len(uploaded_files) > 0:
        for f in uploaded_files:
            file_label = f"{f.name} ({round(f.size/1024/1024,1)}MB)"
            user_bubbles.append({
                "type": "file",
                "content": file_label,
                "timestamp": msg_time
            })

    # 保存到历史
    st.session_state["history"].append({
        "role": "user",
        "bubbles": user_bubbles,
        "timestamp": msg_time
    })

    # AI回复
    ai_reply = {
        "role": "ai",
        "bubbles": [{
            "type": "text",
            "content": "收到！文件与问题已提交，正在处理...",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }],
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    st.session_state["history"].append(ai_reply)

    # 清空输入框（通过设置 flag，而不是 session_state 赋值！）
    st.session_state["clear_input"] = True

    # 文件上传控件 Streamlit 无法强制清空
    st.success("发送成功！如需继续请移除文件或输入新问题。")

# 聊天历史气泡显示
for msg in st.session_state["history"]:
    for bubble in msg["bubbles"]:
        wrap_class = "bubble-wrap"
        if msg["role"] == "user":
            bubble_html = f"""
            <div class="{wrap_class}">
                <div class="user-bubble">{bubble['content']}</div>
                <div class="bubble-meta" style="text-align:right;">你 · {bubble['timestamp']}</div>
            </div>
            """
        else:
            bubble_html = f"""
            <div class="{wrap_class}">
                <div class="ai-bubble">{bubble['content']}</div>
                <div class="bubble-meta" style="text-align:left;">AI · {bubble['timestamp']}</div>
            </div>
            """
        st.markdown(bubble_html, unsafe_allow_html=True)

# 上传提示
if not can_send:
    st.info("请上传文件或输入问题后再发送")
