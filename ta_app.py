import streamlit as st
import PyPDF2
import google.generativeai as genai

# --- ✨ 앱 설정 ---
st.set_page_config(page_title="UCLA 과목 통합 AI 조교", page_icon="🎓", layout="wide")

# --- 🔑 Gemini AI 설정 ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3-flash-preview')
except:
    st.error("API 키를 확인해주세요.")

# --- 📂 과목 리스트 & 세션 상태 초기화 ---
# Jace의 이번 학기 시간표 반영
COURSES = ["MATH 32B", "MATH 33A", "CHEM 30A", "STATS 13", "LING 1"]

if 'course_data' not in st.session_state:
    st.session_state['course_data'] = {course: {"notes": "", "chat_history": []} for course in COURSES}

# --- ⬅️ 사이드바: 과목 선택 ---
st.sidebar.title("📌 이번 학기 수강 목록")
selected_course = st.sidebar.radio("공부할 과목을 선택하세요:", COURSES)

# --- 🖥️ 메인 화면 ---
st.title(f"📖 {selected_course} AI 전담 학습관")
st.write(f"현재 **{selected_course}** 섹션에서 학습 중입니다.")

# 탭 구성: 노트 관리, AI 질의응답
tab_note, tab_chat = st.tabs(["📄 노트 업로드 및 분석", "💬 AI와 대화하며 이해하기"])

# ==========================================
# 탭 1: 과목별 노트 업로드 및 관리
# ==========================================
with tab_note:
    st.subheader(f"📂 {selected_course} 강의자료 업로드")
    uploaded_file = st.file_uploader(f"{selected_course} PDF 노트를 올려주세요", type=["pdf"], key=f"file_{selected_course}")

    if uploaded_file:
        with st.spinner("노트를 읽어 분석하는 중..."):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted: text += extracted
            
            # 해당 과목 세션에 텍스트 저장
            st.session_state['course_data'][selected_course]['notes'] = text
            st.success(f"{selected_course} 노트가 성공적으로 분석되었습니다!")

    if st.session_state['course_data'][selected_course]['notes']:
        st.info("✅ 현재 업로드된 노트가 있습니다. 이제 'AI와 대화하기' 탭에서 질문할 수 있습니다.")
        if st.button("🗑️ 노트 초기화"):
            st.session_state['course_data'][selected_course]['notes'] = ""
            st.rerun()

# ==========================================
# 탭 2: 과목별 AI 질의응답 (RAG)
# ==========================================
with tab_chat:
    st.subheader(f"💬 {selected_course} AI 튜터")
    
    # 해당 과목의 채팅 기록 불러오기
    chat_history = st.session_state['course_data'][selected_course]['chat_history']
    notes_content = st.session_state['course_data'][selected_course]['notes']

    # 채팅 메시지 표시
    for message in chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input(f"{selected_course}에 대해 무엇이든 물어보세요!"):
        # 사용자 메시지 표시 및 저장
        with st.chat_message("user"):
            st.markdown(user_input)
        chat_history.append({"role": "user", "content": user_input})

        # AI 답변 생성
        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):
                # 노트를 컨텍스트로 포함한 프롬프트 구성
                context = f"과목명: {selected_course}\n\n[업로드된 노트 내용]\n{notes_content[:5000]}" if notes_content else "업로드된 노트 없음"
                
                full_prompt = f"""
                너는 {selected_course} 과목을 가르치는 친절하고 전문적인 UCLA 조교야. 
                아래 제공된 '노트 내용'을 바탕으로 학생의 질문에 답변해줘. 
                만약 노트에 없는 내용이라면 너의 전문 지식을 동원해 설명해주되, 노트와 연관지어 답변해줘.
                
                {context}
                
                질문: {user_input}
                """
                
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                chat_history.append({"role": "assistant", "content": response.text})
        
        # 채팅 기록 세션에 업데이트
        st.session_state['course_data'][selected_course]['chat_history'] = chat_history