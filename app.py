import streamlit as st
import requests
import json

# 페이지 설정
st.set_page_config(page_title="우리나라 지리 척척박사님", page_icon="🌏")

st.title("🌏 척척박사 지리 선생님")
st.caption("궁금한 지역 이름을 입력하면 선생님이 친절하게 알려줄게요! (예: 독도, 서울, 부산)")

# 사이드바에서 API 키 입력 받기
with st.sidebar:
    api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
    st.markdown("[Google AI Studio](https://aistudio.google.com/)에서 키를 발급받으세요.")

# 시스템 프롬프트 설정 (선생님 페르소나 & 지리 정보 미션)
system_instruction = """
당신은 아이들을 정말 사랑하는 5년 차 베테랑 유치원 선생님입니다. 
다음 원칙을 지켜서 답변해주세요:
1. 말투: "친구들~", "~해요" 처럼 아주 친절하고 다정하게 존댓말을 사용하세요.
2. 필수: 답변에는 반드시 이모지(😊, 🌳, 🌊 등)를 아주 풍부하게 섞어서 사용하세요.
3. 임무: 사용자가 '지역 이름'을 물어보면, 초등학생 눈높이에 맞춰서 다음 내용을 설명해 주세요.
   - 📍 위치: 어디에 있는지
   - ✨ 특징: 무엇이 유명한지, 어떤 재미있는 점이 있는지
   - 👨‍👩‍👧‍👦 인구수: 대략 얼마나 많은 사람이 살고 있는지 (어려운 숫자는 '아주 많은 사람' 등으로 비유해도 좋아요)
4. 만약 지리적 지명이 아닌 질문을 하면 "선생님은 지리 공부만 도와줄 수 있어요~ 다른 지역을 물어봐 줄래요? 🗺️"라고 답해주세요.
"""

# 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("지역 이름을 입력해볼까요?"):
    # 1. 사용자 메시지 표시 및 저장
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. API 키 확인
    if not api_key:
        st.error("선생님을 만나려면 API 키가 필요해요! 왼쪽 사이드바에 입력해주세요. 🔑")
        st.stop()

    # 3. Gemini API 요청 (System Instruction 포함)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [{
            "parts": [{"text": prompt}] 
        }]
    }

    # 4. 응답 받아오기
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("선생님이 생각하고 있어요... 🤔")
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                result = response.json()
                bot_response = result['candidates'][0]['content']['parts'][0]['text']
                
                message_placeholder.markdown(bot_response)
                st.session_state.messages.append({"role": "assistant", "content": bot_response})
            else:
                message_placeholder.error(f"오류가 났어요 ㅠㅠ: {response.text}")
        except Exception as e:
            message_placeholder.error(f"문제가 발생했어요: {e}")