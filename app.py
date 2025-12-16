import streamlit as st
import google.generativeai as genai

# [설정] 페이지 기본 구성
# 목적: 학생들이 접속했을 때 'AI 선생님'임을 직관적으로 알 수 있도록 제목과 아이콘 설정
st.set_page_config(
    page_title="초등학생을 위한 AI 선생님",
    page_icon="🎓",
    layout="centered"
)

# [UI] 헤더 및 안내 문구
# 결과: 화면 상단에 큰 제목과 안전 수칙이 표시됨
st.title("🎓 무엇이든 물어보세요! AI 선생님")
st.write("안녕? 학교 공부하다가 모르는 게 생기면 물어봐!")
st.info("비밀(이름, 주소, 전화번호)은 절대 말하면 안 돼요! 쉿! 🤫")

# [보안] API 키 설정 및 예외 처리
# 목적: .streamlit/secrets.toml 파일에서 비밀 키를 안전하게 가져오고, 없을 경우 오류를 방지함
try:
    # Streamlit Cloud 배포 환경과 로컬 환경 모두에서 작동하도록 비밀 키 호출
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    # 키가 설정되지 않았을 때 학생들에게는 보이지 않도록 개발자용 에러 로그만 남김
    st.error("AI 선생님을 부를 수 없어요. (관리자에게 문의: API Key 누락)")
    st.stop()

# [AI 설정] 페르소나(Persona) 및 안전 규칙 정의 (프롬프트 엔지니어링)
# 목적: AI가 무분별한 답변을 하지 않고, 초등학생 눈높이에 맞춰 교육적으로 답변하도록 역할을 부여함
system_instruction = """
당신은 초등학생(8~13세)을 지도하는 친절하고 다정한 'AI 선생님'입니다.
다음 원칙을 철저히 지켜서 답변하세요:

1. [눈높이 교육] 어려운 한자어나 전문 용어 대신, 초등학생이 이해하기 쉬운 비유와 예시를 사용하세요.
2. [안전 제일] 폭력, 선정성, 혐오, 범죄와 관련된 질문은 "그건 대답해주기 어려운 질문이에요. 선생님이나 부모님께 여쭤볼까요?"라고 단호하지만 부드럽게 거절하세요.
3. [개인정보 보호] 학생이 이름, 학교, 전화번호 등을 말하면 "개인정보는 소중해요. 여기에 적으면 안 돼요."라고 교육하세요.
4. [사고력 확장] 정답을 바로 알려주기보다는, 학생이 스스로 생각할 수 있도록 힌트를 주거나 되물어보세요. (예: "좋은 질문이네! OO이는 어떻게 생각하니?")
5. [공감과 격려] 학생의 질문에 칭찬을 먼저 해주고(예: "정말 기발한 생각이구나!"), 긍정적인 태도로 대화하세요.
"""

# [모델 로드] 설정한 페르소나를 적용하여 AI 모델 준비
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # 속도가 빠르고 효율적인 모델 선택
    system_instruction=system_instruction
)

# [기능] 대화 내용 기억하기 (Session State)
# 목적: 사용자가 새로고침하더라도 이전 대화 흐름이 끊기지 않고 유지되도록 저장소 생성
if "messages" not in st.session_state:
    st.session_state.messages = []

# [UI] 채팅 기록 표시
# 결과: 저장된 대화 내용을 화면에 순서대로 말풍선 형태로 보여줌
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# [상호작용] 사용자 질문 입력 처리
# 목적: 사용자가 질문을 입력하고 엔터를 눌렀을 때만 반응하도록 함
if prompt := st.chat_input("질문을 입력하고 엔터를 치세요..."):
    
    # 1. 사용자의 질문을 화면에 표시하고 저장
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. AI의 답변 생성 및 표시
    with st.chat_message("assistant"):
        message_placeholder = st.empty() # 답변이 타이핑되듯 나오게 하기 위한 빈 공간
        full_response = ""
        
        try:
            # AI에게 질문 전달 (현재 질문만 전달하여 토큰 절약 및 안전성 확보)
            response = model.generate_content(prompt)
            full_response = response.text
            
            # 답변 출력
            message_placeholder.markdown(full_response)
        except Exception as e:
            # 오류 발생 시 친절한 안내 메시지 출력
            full_response = "미안해, 잠깐 연결이 끊겼어. 다시 한번 말해줄래?"
            message_placeholder.markdown(full_response)
    
    # 3. AI의 답변을 대화 기록에 저장
    st.session_state.messages.append({"role": "assistant", "content": full_response})