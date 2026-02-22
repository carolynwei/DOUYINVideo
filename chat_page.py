"""  
对话创作助手页面
提供沉浸式聊天界面，支持连续对话创作剧本
"""

import streamlit as st
import time
import requests
import json
from db_manager import get_user_credits, deduct_credits, save_message, load_messages, clear_messages

def call_deepseek_chat(messages, api_key, model_id="deepseek-chat"):
    """调用 DeepSeek API 进行对话"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"❌ API 调用失败: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"❌ 调用异常: {str(e)}"

def render_chat_page(user_id, llm_api_key, model_id, model_cost):
    """渲染对话创作页面"""
    
    st.subheader("💬 对话创作助手")
    st.caption("💡 和AI自然对话，轻松创作爆款剧本。AI会记住你说的每一句话！")
    
    # 🔥 核心：处理用户登录与历史记录加载
    # 使用 session_state 记录当前正在聊天的用户，防止重复加载数据库
    if "current_chat_user" not in st.session_state:
        st.session_state.current_chat_user = None
    
    # 系统提示词：让AI扮演视频创作助手
    system_prompt = {
        "role": "system",
        "content": """你是一个专业的短视频创作助手，擅长：
1. 帮助用户创作抖音、快手等平台的爆款视频脚本
2. 提供创意的分镜建议和画面描述
3. 优化文案的节奏、情绪和吸引力
4. 结合热点趋势和用户心理

回复风格：
- 简洁有力，直接给出实用建议
- 适当使用emoji增加表达力
- 当用户需要完整剧本时，以JSON格式输出分镜内容

请始终记住对话上下文，给出连贯的建议。"""
    }
    
    # 只有当用户刚登录，或者切换了账号时，才去数据库拉取历史记录
    if st.session_state.current_chat_user != user_id:
        st.session_state.current_chat_user = user_id
        db_history = load_messages(user_id)
        
        # 如果数据库没记录，给个默认欢迎语；如果有，直接赋给 session_state
        if not db_history:
            st.session_state.chat_messages = [
                system_prompt,
                {"role": "assistant", "content": f"你好 {user_id}！我是你的AI创作助手。🎬\n\n你可以：\n- 💡 告诉我视频主题，我帮你写剧本\n- ✨ 聊聊你的创意想法\n- 🔥 让我优化你的文案\n\n今天想创作什么内容？"}
            ]
            # 保存欢迎语到数据库
            save_message(user_id, "assistant", st.session_state.chat_messages[1]["content"])
        else:
            # 从数据库恢复历史记录，并在最前面加上系统提示词
            st.session_state.chat_messages = [system_prompt] + db_history
            st.success(f"📦 已从数据库恢复 {len(db_history)} 条历史对话记录")
    
    # --- 2. 侧边栏控制 ---
    with st.sidebar:
        st.divider()
        st.subheader("💬 对话管理")
        
        if st.button("🗑️ 清空对话历史", use_container_width=True):
            # 清空数据库记录
            clear_messages(user_id)
            
            # 重置界面状态
            st.session_state.chat_messages = [
                system_prompt,
                {"role": "assistant", "content": "记忆已清空，我们重新开始吧！🚀"}
            ]
            # 保存新的欢迎语到数据库
            save_message(user_id, "assistant", st.session_state.chat_messages[1]["content"])
            st.rerun()
        
        st.metric("📝 当前对话轮数", len(st.session_state.chat_messages) // 2)
        st.caption(f"💰 当前余额: {get_user_credits(user_id)} 积分")
        st.caption(f"🧠 当前模型: {model_id}")
        st.caption(f"💸 单次消耗: {model_cost} 积分")
    
    # --- 3. 渲染历史对话记录 ---
    # 过滤掉 system 消息，只显示 user 和 assistant 的对话
    for msg in st.session_state.chat_messages:
        if msg["role"] != "system":  # 不显示系统提示词
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    # --- 4. 接收用户输入并生成回复 ---
    if prompt := st.chat_input("在这里输入... (例如: 帮我写一个关于职场焦虑的视频剧本)"):
        
        # a. 检查积分
        if not deduct_credits(user_id, model_cost):
            st.error(f"❌ 积分不足！当前操作需要 {model_cost} 积分。请明日签到或更换低消耗模型。")
            st.stop()
        
        # b. 记录用户的输入 (界面 + 数据库)
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        save_message(user_id, "user", prompt)  # 🔥 存入数据库
        
        # c. 触发 AI 回复逻辑
        with st.chat_message("assistant"):
            with st.spinner(f"正在使用 {model_id} 思考中... (消耗 {model_cost} 积分)"):
                
                # 🔥 真实的 API 调用：将整个历史对话传给模型
                ai_response = call_deepseek_chat(
                    messages=st.session_state.chat_messages,
                    api_key=llm_api_key,
                    model_id=model_id
                )
                
                st.markdown(ai_response)
        
        # d. 记录 AI 的回复 (界面 + 数据库)
        st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
        save_message(user_id, "assistant", ai_response)  # 🔥 存入数据库
        
        # e. 显示积分扣除提示
        st.success(f"✅ 已扣除 {model_cost} 积分，当前余额: {get_user_credits(user_id)} 积分")
        st.rerun()  # 刷新页面显示最新积分
