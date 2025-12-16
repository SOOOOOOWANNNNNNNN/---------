import streamlit as st
import time

# [설정] 페이지 기본 구성
st.set_page_config(
    page_title="우리반 안전 지킴이 챗봇",
    page_icon="⛑️",
    layout="centered"
)

# [UI] 헤더 영역
st.title("⛑️ 4학년 안전 교육: 지진과 화산")
st.write("지진이나 화산에 대해 궁금한 점을 물어보세요! (예: 지진이 뭐야? 대피는 어떻게 해?)")
st.info("💡 이 챗봇은 정해진 질문에만 정확하게 대답하도록 만들어졌습니다.")

# [데이터] 규칙 기반 AI를 위한 지식 데이터베이스 (Key-Value 방식)
# 목적: 외부 AI 없이 빠르고 정확한 답변을 제공하며, 오개념을 방지함.
knowledge_base = {
    "지진": "지진이란 땅이 지구 내부의 힘을 받아 흔들리거나 갈라지는 현상을 말해요.",
    "화산": "화산은 땅속 깊은 곳에 있던 마그마가 가스와 함께 분출하여 만들어진 산을 말해요.",
    "마그마": "마그마는 땅속 깊은 곳에서 암석이 녹아 액체처럼 된 상태를 말해요.",
    "용암": "용암은 마그마가 지표면 밖으로 나와서 가스가 빠져나가고 흐르는 것을 말해요.",
    "규모": "규모는 지진 자체의 힘의 크기를 나타내는 단위예요. 숫자가 클수록 강력한 지진입니다.",
    "진도": "진도는 어떤 장소에서 사람이 느끼는 흔들림의 정도나 피해 정도를 나타내는 기준이에요.",
    "대피": "지진이 나면 책상 아래로 들어가 머리를 보호하고, 흔들림이 멈추면 운동장 같은 넓은 곳으로 대피해야 해요.",
    "가방": "대피할 때는 두꺼운 책이나 가방으로 머리를 보호하는 것이 중요해요.",
    "승강기": "지진이나 화재 발생 시 승강기(엘리베이터)는 절대 타면 안 돼요! 계단을 이용하세요.",
    "백두산": "백두산은 우리나라의 대표적인 활화산이에요. 지금은 쉬고 있지만 언제든 다시 분화할 수 있어요."
}

# [기능] 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# [UI] 이전 대화 내용 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# [로직] 사용자 입력 처리 및 답변 생성
if user_input := st.chat_input("궁금한 단어나 내용을 입력하세요..."):
    
    # 1. 사용자 질문 표시
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 2. 챗봇 답변 로직 (키워드 매칭 방식)
    # 목적: 사용자의 문장에 핵심 키워드가 들어있는지 확인하여 답변 선택
    response = ""
    found = False
    
    # 입력된 문장에서 키워드 찾기
    for keyword, answer in knowledge_base.items():
        if keyword in user_input:
            response = f"**[{keyword}]**에 대해 물어봤구나!\n\n{answer}"
            found = True
            break
    
    # 키워드를 찾지 못한 경우
    if not found:
        response = "미안해, 아직 배우지 않은 내용이라 잘 모르겠어. 😅\n\n**'지진', '화산', '대피', '마그마', '승강기'** 같은 단어를 포함해서 물어봐 줄래?"

    # 3. 답변 표시 (타이핑 효과)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        # 약간의 딜레이를 주어 생각하는 척 연출
        time.sleep(0.5)
        message_placeholder.markdown(response)
        
    st.session_state.messages.append({"role": "assistant", "content": response})