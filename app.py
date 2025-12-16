import streamlit as st
import google.generativeai as genai

# [1] 페이지 설정
st.set_page_config(page_title="우리 반 AI 선생님", page_icon="🤖")
st.title("🤖 무엇이든 물어보세요 (초등학생 전용)")
st.caption("안전하고 정확한 정보를 알려주는 AI 선생님입니다.")

# [2] API 키 설정
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("API 키가 설정되지 않았습니다.")
    st.stop()

# [3] 안전 규칙 프롬프트 (내용은 동일)
safety_system_prompt = """
당신은 친절하고 지혜로운 초등학교 선생님 AI입니다. 다음 원칙을 반드시 지키세요:
1. [답변 수준]: 초등학교 3~6학년 학생이 이해할 수 있는 쉬운 어휘와 친절한 존댓말을 사용하세요.
2. [안전 관리]: 폭력적, 선정적, 혐오 표현, 범죄 모의 등 교육적으로 부적절한 질문이 들어오면 정중히 거절하세요.
3. [정보의 신뢰성]: 답변은 검증된 교과서적 사실에 기반해야 합니다.
4. [교육적 유도]: 답을 바로 알려주기보다 힌트를 주어 스스로 생각하게 하세요.
"""

# [4] 모델 설정 (오류 방지를 위해 system_instruction 제거)
# 구버전 라이브러리에서도 100% 작동하도록 기본 설정만 사용합니다.
model = genai.GenerativeModel("gemini-1.5-flash")

# [5] 세션 상태 초기화 (여기가 핵심!)
# 시스템 설정을 '채팅 기록'의 맨 처음에 강제로 넣어서, AI가 선생님 역할을 하도록 만듭니다.
if "messages" not in st.session_state:
    st.session_state.messages = [
        # 사용자가 말한 것처럼 시스템 프롬프트를 먼저 주입
        {"role": "user", "content": safety_system_prompt},
        # AI가 알겠다고 대답한 것처럼 기록 조작
        {"role": "model", "content": "네, 알겠습니다. 저는 초등학교 선생님으로서 학생들의 눈높이에 맞춰 친절하고 안전하게 답변하겠습니다."}
    ]

# [6] 대화 기록 표시 (첫 번째 시스템 설정 대화는 화면에 안 보이게 숨김)
# list slicing [2:]를 사용하여 사용자가 실제로 입력한 대화부터 보여줍니다.
for message in st.session_state.messages[2:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# [7] 사용자 입력 및 답변 처리
if prompt := st.chat_input("궁금한 것을 물어보세요!"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("선생님이 생각하고 있어요..."):
            try:
                # 저장된 모든 대화 기록(시스템 설정 포함)을 AI에게 전달
                chat_history = [
                    {"role": m["role"], "parts": [m["content"]]}
                    for m in st.session_state.messages
                ]
                
                # generate_content로 변경 (호환성이 가장 좋음)
                response = model.generate_content(chat_history)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "model", "content": response.text})
            except Exception as e:
                # 오류 메시지를 좀 더 자세히 출력
                st.error(f"오류가 발생했습니다: {e}")