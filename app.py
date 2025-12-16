import streamlit as st
import google.generativeai as genai

# -------------------------------------------------------------------------
# [1. 페이지 기본 설정]
# 초등학생들이 친근감을 느낄 수 있도록 아이콘과 제목을 설정합니다.
# -------------------------------------------------------------------------
st.set_page_config(page_title="우리 반 AI 선생님", page_icon="🤖")

st.title("🤖 무엇이든 물어보세요 (초등학생 전용)")
st.caption("안전하고 정확한 정보를 알려주는 AI 선생님입니다.")

# -------------------------------------------------------------------------
# [2. Gemini API 설정 및 보안]
# GitHub에 API 키가 노출되면 안 되므로, Streamlit의 'Secrets' 기능을 사용해
# 안전하게 키를 불러옵니다. (코드에 직접 키를 적지 않습니다.)
# -------------------------------------------------------------------------
# 배포 전 로컬 테스트 시에는 오류 방지를 위한 예외 처리를 해둡니다.
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    st.error("API 키가 설정되지 않았습니다. 스트림릿 설정에서 키를 추가해주세요.")
    st.stop()

# -------------------------------------------------------------------------
# [3. AI 페르소나(인격) 및 안전 규칙 설정] - **가장 중요한 부분**
# 사용자의 요구사항인 '초등 수준', '부적절 질문 차단', '공신력 있는 정보'를
# 시스템 프롬프트(System Instruction)로 정의합니다.
# -------------------------------------------------------------------------
safety_system_prompt = """
당신은 친절하고 지혜로운 초등학교 선생님 AI입니다. 다음 원칙을 반드시 지키세요:

1. [답변 수준]: 초등학교 3~6학년 학생이 이해할 수 있는 쉬운 어휘와 친절한 존댓말을 사용하세요. 어려운 전문 용어는 쉽게 풀어서 설명하세요.
2. [안전 관리]: 폭력적, 선정적, 혐오 표현, 범죄 모의 등 교육적으로 부적절한 질문이 들어오면 "그 질문에는 답변해 줄 수 없어요. 우리 수업과 관련된 즐거운 이야기를 해볼까요?"라고 단호하지만 부드럽게 거절하세요.
3. [정보의 신뢰성]: 답변은 검증된 교과서적 사실과 백과사전 지식에 기반해야 합니다. 출처가 불분명한 인터넷 유머나 뜬소문은 사실인 것처럼 말하지 마세요. 확실하지 않은 내용은 "그 부분은 선생님도 더 찾아봐야 할 것 같아요"라고 솔직하게 말하세요.
4. [교육적 유도]: 학생이 단순히 답만 베끼려고 하면, 바로 정답을 주기보다는 스스로 생각할 수 있는 힌트를 먼저 주세요.
"""

# 모델 초기화 (위에서 만든 선생님 규칙을 적용)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=safety_system_prompt
)

# -------------------------------------------------------------------------
# [4. 대화 기록(세션) 관리]
# 사용자가 새로고침하더라도 이전 대화 내용이 사라지지 않도록 저장합니다.
# -------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 저장된 이전 대화들을 화면에 표시 (채팅 내역 유지)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------------------------------------------------------------
# [5. 사용자 입력 및 답변 생성 로직]
# 학생이 질문을 입력하면 AI 선생님이 설정된 규칙에 따라 답변합니다.
# -------------------------------------------------------------------------
if prompt := st.chat_input("궁금한 것을 물어보세요!"):
    # 1) 학생의 질문을 화면에 표시하고 기록에 저장
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2) AI 선생님에게 질문 전달 및 답변 생성
    with st.chat_message("assistant"):
        with st.spinner("선생님이 생각하고 있어요..."):
            try:
                # 대화 맥락을 유지하며 답변 생성
                chat = model.start_chat(history=[
                    {"role": m["role"], "parts": [m["content"]]} 
                    for m in st.session_state.messages[:-1] # 현재 질문 제외한 이전 기록
                ])
                response = chat.send_message(prompt)
                
                # 답변 출력
                st.markdown(response.text)
                
                # 답변을 기록에 저장
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
                