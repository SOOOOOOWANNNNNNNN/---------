import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# --------------------------------------------------------------------------
# [목적] .env 파일 또는 스트림릿 클라우드의 Secrets에서 환경 변수(API Key)를 불러옵니다.
# [결과] 소스 코드에 비밀번호를 노출하지 않고 안전하게 키를 관리할 수 있습니다.
# --------------------------------------------------------------------------
load_dotenv() 

# --------------------------------------------------------------------------
# [목적] 웹 애플리케이션의 탭 이름, 아이콘, 기본 레이아웃을 설정합니다.
# [결과] 브라우저 상단 탭에 '지리 척척박사님'이 표시되고, 지구 아이콘이 나타납니다.
# --------------------------------------------------------------------------
st.set_page_config(page_title="우리나라 지리 척척박사님", page_icon="🌏")

st.title("🌏 척척박사 지리 선생님")
st.caption("궁금한 지역을 입력하거나, 왼쪽에서 골라보세요! (예: 독도, 서울)")

# --------------------------------------------------------------------------
# [목적] 환경변수에서 API 키를 가져옵니다. (로컬: .env / 배포: Secrets)
# [결과] 사용자가 키를 직접 입력하지 않아도 프로그램이 자동으로 인증 정보를 인식합니다.
# --------------------------------------------------------------------------
api_key = os.getenv("GEMINI_API_KEY")

# --------------------------------------------------------------------------
# [목적] 왼쪽 사이드바에 대표 지역 선택 기능을 추가하여 사용자 편의성을 높입니다.
# [결과] 타자가 익숙하지 않은 학생들도 클릭만으로 질문할 수 있는 메뉴가 왼쪽에 생깁니다.
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("🗺️ 지역 골라보기")
    selected_location = st.selectbox(
        "궁금한 지역을 선택하고 '질문하기'를 눌러보세요!",
        ["직접 입력", "독도", "제주도", "경주", "서울", "부산", "평양"]
    )
    is_sidebar_clicked = st.button("이 지역 질문하기")

# --------------------------------------------------------------------------
# [목적] AI에게 '친절한 유치원 선생님' 역할을 부여하고 답변 형식을 지정합니다.
# [결과] AI가 기계적인 정보 대신, 아이들 눈높이에 맞춘 다정한 말투와 이모지를 사용합니다.
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
# [목적] 새로고침 시 대화 내용이 사라지는 것을 방지하기 위해 저장소를 초기화합니다.
# [결과] 이전 대화 기록이 유지되어 문맥이 끊기지 않는 채팅 경험을 제공합니다.
# --------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --------------------------------------------------------------------------
# [목적] 저장된 대화 기록을 화면에 순서대로 다시 표시합니다.
# [결과] 사용자와 AI가 주고받은 말풍선들이 채팅창 형태로 유지됩니다.
# --------------------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --------------------------------------------------------------------------
# [목적] 직접 입력과 사이드바 선택, 두 가지 방식을 통합하여 질문을 처리합니다.
# [결과] 어디서 입력을 하든 동일하게 AI에게 질문이 전달됩니다.
# --------------------------------------------------------------------------
prompt = None
if user_input := st.chat_input("지역 이름을 입력해볼까요?"):
    prompt = user_input
elif is_sidebar_clicked and selected_location != "직접 입력":
    prompt = selected_location

if prompt:
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # API 키 확인
    if not api_key:
        st.error("API 키가 설정되지 않았습니다. Secrets 설정을 확인해주세요.")
        st.stop()

    # --------------------------------------------------------------------------
    # [목적] 가장 안정적인 Gemini Pro 모델을 호출하여 API 통신을 수행합니다.
    # [결과] 404 오류를 방지하고 AI 모델이 요청을 받아들입니다.
    # --------------------------------------------------------------------------
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": system_instruction + "\n\n질문: " + prompt}]}]
    }

    # 응답 처리 및 예외 처리
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("선생님이 생각하고 있어요... 🤔")
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            # [목적] 응답 상태 코드에 따라 성공과 실패(429, 404 등)를 구분하여 처리합니다.
            if response.status_code == 200:
                result = response.json()
                bot_response = result['candidates'][0]['content']['parts'][0]['text']
                message_placeholder.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
            
            elif response.status_code == 429:
                # [결과] 요청 횟수 초과 시 사용자에게 대기하라는 안내 메시지를 띄웁니다.
                message_placeholder.error("질문이 너무 많아요! 1분만 쉬었다가 다시 물어봐주세요. 😅")
            
            else:
                message_placeholder.error(f"오류가 발생했습니다: {response.status_code}")
                
        except Exception as e:
            message_placeholder.error(f"네트워크 문제가 발생했습니다: {e}")