import streamlit as st
import google.generativeai as genai

# --- [설정] 페이지 기본 구성 ---
# 브라우저 탭 제목과 아이콘을 설정하여 학생들에게 친근한 느낌을 줌
st.set_page_config(
    page_title="AI 선생님 챗봇",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 궁금한 내용을 물어보세요!")
st.write("안녕? 나는 AI 선생님이야. 학교 공부나 궁금한 점이 있으면 무엇이든 물어봐!")
st.info("💡 개인정보(이름, 전화번호 등)는 절대 입력하면 안 돼요!")

# --- [핵심] AI 모델 및 안전 프롬프트 설정 ---

# 1. API 키 불러오기: .streamlit/secrets.toml 파일에 저장된 비밀 키를 안전하게 가져옴
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.error("API 키 설정 오류입니다. secrets.toml 파일을 확인해주세요.")
    st.stop()

# 2. 시스템 프롬프트 (AI의 페르소나 및 안전 규칙 정의)
# 이 부분이 요청하신 '안전하고 공신력 있는 답변'을 만드는 핵심입니다.
SYSTEM_PROMPT = """
당신은 초등학생들을 위한 친절하고 지혜로운 AI 교사 'AI 쌤'입니다.
다음 규칙을 반드시 준수하여 대답하십시오:

1.  **대상 및 어조:** 사용자는 초등학생(8세~13세)입니다. 존댓말을 사용하고, 어려운 한자어나 전문 용어 대신 쉬운 어휘와 비유를 사용하여 친절하게 설명하세요.
2.  **안전 및 윤리(가장 중요):** 폭력, 혐오 표현, 성적인 내용, 자해, 범죄, 약물 등 부적절한 주제에 대한 질문을 받으면 절대 답을 제공하지 마십시오. 대신 "그런 질문에는 대답해주기 어려워요. 부모님이나 학교 선생님께 여쭤보는 건 어떨까요?"라고 부드럽게 거절하세요.
3.  **개인정보 보호:** 사용자가 자신의 이름, 주소, 전화번호 등을 말하면 "개인정보는 소중해요. 여기에 적으면 안 돼요."라고 알려주세요.
4.  **공신력 및 정확성:** 확인된 사실에 기반하여 정확한 정보를 제공하세요. 잘 모르는 내용이거나 의견이 갈리는 내용은 솔직하게 모른다고 답하거나 다양한 관점이 있음을 알려주세요. 숙제를 대신 다 해주는 것보다는 스스로 생각할 수 있도록 힌트를 주는 방향으로 유도하세요.
5.  **긍정적 강화:** 학생의 질문 의도를 칭찬하고 격려해주세요.
"""

# 3. AI 모델 초기화: 'gemini-pro' 모델을 사용하며, 위에서 정의한 시스템 프롬프트를 주입합니다.
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # 빠르고 효율적인 최신 모델 사용
    system_instruction=SYSTEM_PROMPT
)


# --- [UI/UX] 채팅 인터페이스 구현 ---

# 1. 세션 상태 초기화: 대화 내용을 기억하기 위해 Streamlit의 session_state를 사용합니다.
# 앱이 새로고침 되어도 기존 대화 내용이 유지되도록 합니다.
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 2. 이전 대화 기록 표시: 저장된 대화 내용을 화면에 순서대로 출력합니다.
# 사용자와 AI의 메시지를 구분하여 보여줍니다.
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. 사용자 입력 처리 및 AI 응답 생성
# 화면 하단에 채팅 입력창을 만들고 사용자가 엔터를 누르면 실행됩니다.
if user_query := st.chat_input("여기에 질문을 입력하고 엔터를 누르세요..."):
    
    # [사용자 화면] 입력한 질문을 화면에 표시합니다.
    with st.chat_message("user"):
        st.markdown(user_query)
    # 대화 기록에 사용자 질문을 추가합니다.
    st.session_state.chat_history.append({"role": "user", "content": user_query})

    # [AI 처리] AI가 답변을 생각하는 동안 로딩 표시를 보여줍니다.
    with st.chat_message("assistant"):
        message_placeholder = st.empty() # 답변이 들어갈 빈 공간을 만듭니다.
        message_placeholder.markdown("AI 선생님이 답변을 생각 중이에요... 🤔")
        
        try:
            # [핵심 로직] AI에게 질문을 보내고 답변을 받습니다.
            # 기존 대화 내역을 함께 보내 문맥을 이해하게 할 수도 있지만, 
            # 안전을 위해 매번 새로운 질문으로 처리하는 것이 지금 단계에선 더 안전할 수 있습니다. 
            # 여기서는 단순화를 위해 현재 질문만 보냅니다.
            response = model.generate_content(user_query)
            ai_response_text = response.text
            
            # [AI 화면] 생성된 답변을 화면에 표시합니다.
            message_placeholder.markdown(ai_response_text)
            
            # 대화 기록에 AI 답변을 추가합니다.
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response_text})
            
        except Exception as e:
            # API 호출 중 에러 발생 시 사용자에게 안내합니다.
            message_placeholder.error("미안해요, 잠시 연결에 문제가 생겼어요. 다시 질문해 줄래요?")