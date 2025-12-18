import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# --------------------------------------------------------------------------
# [목적] .env 파일에 저장된 환경 변수(API Key 등)를 불러옵니다.
# [결과] 코드 안에 비밀번호(API Key)를 적지 않아도, 컴퓨터가 알아서 .env 파일을 찾아 키를 가져옵니다.
# --------------------------------------------------------------------------
load_dotenv() 

# --------------------------------------------------------------------------
# [목적] 웹사이트의 제목, 아이콘 등 기본 구성을 설정합니다.
# [결과] 브라우저 탭에 '지리 척척박사님'이 뜨고, 아이콘이 지구 모양(🌏)으로 바뀝니다.
# --------------------------------------------------------------------------
st.set_page_config(page_title="우리나라 지리 척척박사님", page_icon="🌏")

st.title("🌏 척척박사 지리 선생님")
st.caption("궁금한 지역을 입력하거나, 왼쪽에서 골라보세요! (예: 독도, 서울)")


# --------------------------------------------------------------------------
# [목적] 환경변수에서 API 키를 가져옵니다.
# [결과] 사용자가 매번 키를 입력할 필요 없이, 미리 설정된 키로 챗봇이 작동합니다.
# --------------------------------------------------------------------------
api_key = os.getenv("GEMINI_API_KEY")


# --------------------------------------------------------------------------
# [목적] 왼쪽 사이드바에 '대표 지역 선택창'을 만듭니다.
# [결과] 사용자가 타자를 치기 어려울 때, 목록에서 '독도', '제주도' 등을 클릭해서 질문할 수 있습니다.
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("🗺️ 지역 골라보기")
    # 사용자가 선택할 수 있는 지역 목록을 만듭니다.
    selected_location = st.selectbox(
        "궁금한 지역을 선택하고 '질문하기'를 눌러보세요!",
        ["직접 입력", "독도", "제주도", "경주", "서울", "부산", "평양"]
    )
    
    # [목적] 선택창의 값이 바뀔 때마다 실행되는 것이 아니라, 버튼을 눌렀을 때 질문이 전송되게 합니다.
    # [결과] '질문하기' 버튼을 누르면 해당 지역에 대한 설명이 채팅창에 뜹니다.
    is_sidebar_clicked = st.button("이 지역 질문하기")


# --------------------------------------------------------------------------
# [목적] AI 선생님의 말투와 역할(페르소나)을 상세하게 설정합니다.
# [결과] AI가 기계적인 답변 대신, 이모지를 섞은 친절한 유치원 선생님 말투로 지리 정보를 설명합니다.
# --------------------------------------------------------------------------
system_instruction = """
당신은 아이들을 정말 사랑하는 5년 차 베테랑 유치원 선생님입니다. 
다음 원칙을 지켜서 답변해주세요:
1. 말투: "친구들~", "~해요" 처럼 아주 친절하고 다정하게 존댓말을 사용하세요.
2. 필수: 답변에는 반드시 이모지(😊, 🌳, 🌊 등)를 아주 풍부하게 섞어서 사용하세요.
3. 임무: 사용자가 '지역 이름'을 물어보면, 초등학생 눈높이에 맞춰서 다음 내용을 설명해 주세요.
   - 📍 위치: 어디에 있는지
   - ✨ 특징: 무엇이 유명한지, 어떤 재미있는 점이 있는지
   - 👨‍👩‍👧‍👦 인구수: 대략 얼마나 많은 사람이 살고 있는지
4. 만약 지리적 지명이 아닌 질문을 하면 "선생님은 지리 공부만 도와줄 수 있어요~ 다른 지역을 물어봐 줄래요? 🗺️"라고 답해주세요.
"""


# --------------------------------------------------------------------------
# [목적] 대화 기록이 사라지지 않도록 저장할 공간(session_state)을 만듭니다.
# [결과] 화면이 새로고침 되어도 이전에 나눈 대화 내용이 유지됩니다.
# --------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------------------------------
# [목적] 저장된 대화 내용을 화면에 순서대로 표시합니다.
# [결과] 카카오톡처럼 사용자와 선생님의 대화가 말풍선으로 나열되어 보입니다.
# --------------------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------------------------------
# [목적] 질문을 받는 두 가지 방법(직접 입력 vs 사이드바 선택)을 처리합니다.
# [결과] 하단 입력창에 글을 쓰거나, 사이드바 버튼을 눌렀을 때 모두 동일하게 AI에게 질문이 전송됩니다.
# --------------------------------------------------------------------------
prompt = None
if user_input := st.chat_input("지역 이름을 입력해볼까요?"):
    prompt = user_input  # 사용자가 직접 타이핑한 경우
elif is_sidebar_clicked and selected_location != "직접 입력":
    prompt = selected_location  # 사이드바에서 선택하고 버튼을 누른 경우


# 질문(prompt)이 들어왔을 때 실행되는 로직
if prompt:
    
    # 1. 사용자 메시지 화면 표시 및 저장
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. API 키 확인 (없으면 경고)
    if not api_key:
        st.error("API 키를 찾을 수 없어요. .env 파일을 확인해주세요! 🔑")
        st.stop()

    # 3. Gemini API 요청 주소 (Gemini 1.5 Pro 사용)
    # 가장 안정적인 'gemini-pro' (1.0 버전) 모델을 사용합니다.
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction}] 
        },
        "contents": [{
            "parts": [{"text": prompt}] 
        }]
    }

    # 4. 응답 수신 및 화면 표시
    # [목적] 구글 서버에서 온 응답을 해석하여 화면에 보여줍니다.
    # [결과] '생각 중...' 로딩 문구 후 선생님의 친절한 답변이 출력됩니다.
    with st.chat_message("assistant"):
        message_placeholder = st.empty() 
        message_placeholder.markdown("선생님이 지도책을 펼치고 있어요... 📖") 
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                result = response.json()
                bot_response = result['candidates'][0]['content']['parts'][0]['text']
                
                message_placeholder.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
            else:
                message_placeholder.error(f"오류가 났어요: {response.status_code}")
        except Exception as e:
            message_placeholder.error(f"문제가 발생했어요: {e}")