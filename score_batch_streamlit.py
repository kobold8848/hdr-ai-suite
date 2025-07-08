import streamlit as st, requests, io, uuid

st.set_page_config(page_title="图片评分对话助手", layout="wide")

# -------- 对话历史持久化 -------- #
if "history" not in st.session_state:
    st.session_state.history = [
        {"role": "assistant", "content": "👋 请上传照片并点击 **提交评分**！"}
    ]

# -------- 渲染历史 -------- #
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------- 上传 & 文字输入 -------- #
u_key = st.session_state.get("u_key", str(uuid.uuid4()))      # 动态 key
uploaded = st.file_uploader(
    "拖拽或选择图片 / RAW / HDR",
    type=["jpg","jpeg","png","tif","tiff","dng","cr2","cr3"],
    key=u_key
)
user_text = st.chat_input("可补充说明（可空）")

# -------- 提交按钮 -------- #
if st.button("提交评分", use_container_width=True):
    # 用户文字
    if user_text:
        st.session_state.history.append({"role":"user","content":user_text})
        with st.chat_message("user"): st.markdown(user_text)

    # 无文件提醒
    if uploaded is None:
        warn = "⚠️ 请先选择文件再提交"
        st.session_state.history.append({"role":"assistant","content":warn})
        st.session_state["u_key"] = str(uuid.uuid4())         # 重置 key
        st.experimental_rerun()

    # 记录上传
    note = f"🖼️ 上传了 **{uploaded.name}**"
    st.session_state.history.append({"role":"user","content":note})
    with st.chat_message("user"): st.markdown(note)

    # 调用后端评分
    try:
        resp = requests.post(
            "http://localhost:8500/score",
            files={"file": (uploaded.name, io.BytesIO(uploaded.getvalue()))},
            timeout=120,
        )
        data = resp.json()
        reply = (
            f"**评分**：{data.get('score','—')}\n"
            f"**建议**：{data.get('suggest','—')}\n"
            f"*({data.get('pipeline','?')}, {data.get('width')}×{data.get('height')})*"
        )
    except Exception as e:
        reply = f"❌ 无法评分：{e}"

    st.session_state.history.append({"role":"assistant","content":reply})
    with st.chat_message("assistant"): st.markdown(reply)

    # ------- 关键：重置 uploader key，彻底清空组件 -------
    st.session_state["u_key"] = str(uuid.uuid4())
    st.experimental_rerun()
