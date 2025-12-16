import streamlit as st
import google.generativeai as genai

# [1] 페이지 설정
st.set_page_config(page_title="우리 반 AI 선생님", page_icon="🤖")
st.title("🤖 무엇이든 물어보세요 (초등학생 전용)")
st.caption("안전하고 정확한 정보를 알려주는 AI 선생님입니다.")

# [2] API 키 설정 (오류 방지 처리)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("API 키가 없습니다. 설정에서 키를 추가해주세요.")
    st.stop()

# [3] 모델 설정 (★가장 중요: 구버전 호환 모델 사용)
# 최신 기능(system_instruction)을 뺐기 때문에 오류가 절대 안 납니다.
model = genai.GenerativeModel('gemini-pro')

# [4] 안전 규칙 (시스템 프롬프트 대용)
# 모델에게 직접 주입할 '가짜 대화 기록'입니다.
safety_prompt = """
당신은 친절하고 지혜로운 초등학교 선생님 AI입니다.
1. 초등학생 수준에 맞춰 쉽고 친절하게 존댓말로 답하세요.
2. 폭력적이거나 선정적인 질문은 정중히 거절하세요.
3. 교과서적인 사실에 기반해서 설명하세요.
"""

# [5] 세션 상태 초기화 (여기서 선생님 역할을 강제로 부여)
if "messages" not in st.session_state:
    st.session_state.messages = [
        # 사용자가 시킨 척하면서 역할을 부여함 (꼼수)
        {"role": "user", "parts": [safety_prompt]},
        # AI가 대답한 척함
        {"role": "model", "parts": ["네, 알겠습니다. 저는 초등학생들을 위한 친절한 선생님입니다."]}
    ]

# [6] 대화 기록 표시
# 맨 처음의 '역할 부여' 대화(0번, 1번)는 화면에 안 보이게 숨김 ([2:] 부터 표시)
for message in st.session_state.messages[2:]:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["parts"][0])

# [7] 사용자 입력 및 답변 처리
if prompt := st.chat_input("궁금한 것을 물어보세요!"):
    # 사용자 질문 표시
    st.chat_message("user").markdown(prompt)
    
    # 대화 기록에 사용자 질문 추가
    st.session_state.messages.append({"role": "user", "parts": [prompt]})

    with st.chat_message("assistant"):
        with st.spinner("선생님이 생각하고 있어요..."):
            try:
                # [핵심] 지금까지의 모든 대화(역할 부여 포함)를 모델에게 보냄
                response = model.generate_content(st.session_state.messages)
                
                # 답변 표시
                st.markdown(response.text)
                
                # 대화 기록에 AI 답변 추가
                st.session_state.messages.append({"role": "model", "parts": [response.text]})
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")