import streamlit as st
import PyPDF2
import google.generativeai as genai

# --- ✨ 앱 기본 설정 ---
st.set_page_config(page_title="나만의 AI 전담 조교", page_icon="👨‍🏫", layout="centered")

# --- 🔑 Gemini AI 설정 ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3-flash-preview')
except Exception as e:
    st.error("API 키 설정에 문제가 있습니다. secrets.toml 파일을 확인해주세요.")

st.title("👨‍🏫 나만의 AI 전담 조교 (Personal TA)")
st.write("학점 관리를 위한 최고의 파트너! 원하는 조교 기능을 선택하세요.")

# --- 📁 기능 분리를 위한 탭 생성 ---
tab1, tab2 = st.tabs(["📚 스마트 PDF 분석기", "♾️ 무한 연습문제 생성기"])

# ==========================================
# 탭 1: 스마트 PDF 분석기 (기존 기능)
# ==========================================
with tab1:
    st.subheader("📚 스마트 PDF 과제 분석기")
    st.write("복잡한 강의 계획서나 과제(Lab) 매뉴얼 PDF를 올려주세요. A+를 위한 핵심만 짚어드립니다!")

    uploaded_file = st.file_uploader("여기에 PDF 파일을 드래그 앤 드롭 하세요", type=["pdf"], key="pdf_uploader")

    if uploaded_file is not None:
        with st.spinner("👀 AI 조교가 PDF 문서를 열심히 읽고 있습니다... ⏳"):
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                document_text = ""
                for page in pdf_reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        document_text += extracted
                        
                st.success("문서 읽기 완료! 이제 과제 분석을 시작할 수 있습니다.")
                
                with st.expander("📄 추출된 원본 텍스트 슬쩍 보기"):
                    st.text(document_text[:1000] + "\n\n... (중략) ...")

                if st.button("🚀 AI 조교에게 A+ 공략법 물어보기", use_container_width=True, type="primary"):
                    with st.spinner("🤔 문서의 행간을 읽으며 감점 포인트를 찾는 중입니다... ✍️"):
                        prompt = f"""
                        너는 대학교의 깐깐하지만 학생을 진심으로 아끼는 A+ 전담 조교(TA)야.
                        다음은 학생이 업로드한 과제 설명서(또는 강의 계획서) PDF의 텍스트야.

                        [문서 내용 시작]
                        {document_text}
                        [문서 내용 끝]

                        이 문서를 꼼꼼하게 분석해서, 학생이 만점을 받기 위해 반드시 알아야 할 내용들을 정리해 줘. 
                        1. 🚨 **핵심 데드라인 및 제출 규칙**
                        2. ✅ **필수 요구사항 (Must-do)**
                        3. ⚠️ **감점 주의사항 (Pitfalls)**
                        4. 💡 **A+ 공략 꿀팁**
                        """
                        response = model.generate_content(prompt)
                        st.markdown("### 👨‍🏫 AI 조교의 과제 분석 리포트")
                        st.info(response.text)
                        
            except Exception as e:
                st.error(f"파일을 읽거나 분석하는 중 오류가 발생했습니다: {e}")

# ==========================================
# 탭 2: 무한 변형 연습문제 생성기 (신규 기능!)
# ==========================================
with tab2:
    st.subheader("♾️ 무한 변형 연습문제 생성기")
    st.write("도무지 풀리지 않거나 연습이 더 필요한 원본 문제를 입력해 보세요. AI가 숫자와 상황만 싹 바꿔서 새로운 문제를 무한으로 만들어 줍니다!")

    # 1. 사용자로부터 원본 문제 입력받기
    original_problem = st.text_area(
        "📝 어려웠던 교재 문제나 튜토리얼 문제를 여기에 복사해 붙여넣으세요:", 
        height=150, 
        placeholder="예시: A 5.0 kg block slides down a frictionless incline at an angle of 30 degrees. Calculate the acceleration of the block."
    )

    # ✨ 신규 기능: 유학생 맞춤형 언어 선택 옵션!
    col_lang1, col_lang2 = st.columns(2)
    q_lang = col_lang1.selectbox("📝 변형 문제 출제 언어", ["영어 (English)", "한국어"])
    a_lang = col_lang2.selectbox("💡 해설 언어", ["한국어", "영어 (English)"])

    # 2. 문제 생성 버튼
    if st.button("🎲 이 문제와 비슷한 변형 문제 만들기", use_container_width=True, type="primary"):
        if not original_problem.strip():
            st.warning("먼저 원본 문제를 입력해 주세요!")
        else:
            with st.spinner("🧠 출제자의 의도를 파악하여 새로운 문제를 만들고 있습니다... ⏳"):
                # ✨ 프롬프트에 사용자가 선택한 언어(q_lang, a_lang)를 강제 주입!
                prompt = f"""
                너는 미국 명문대의 이공계 기초 과목(물리, 화학 등)을 가르치는 1타 강사 조교야.
                학생이 다음 문제를 연습하고 싶어해: 
                "{original_problem}"
                
                이 문제와 **핵심 개념, 사용하는 공식, 난이도는 완벽하게 동일하지만, 숫자 데이터와 현실 상황(Context)을 완전히 다르게 바꾼 변형 문제**를 딱 1개 출제해 줘.
                
                [언어 설정 지침 - 매우 중요!]
                - 변형 문제 언어: 반드시 {q_lang}로 출제할 것.
                - 해설 언어: 반드시 {a_lang}로 친절하게 설명할 것.
                
                반드시 아래의 출력 형식을 엄격하게 지켜서 작성해. (문제와 해설 사이에 반드시 '---' 구분선을 넣어줘)
                
                ### 📝 AI 맞춤형 변형 문제
                [여기에 {q_lang}로 새로운 문제 작성]
                
                ---
                
                ### 💡 단계별 해설 및 정답
                [여기에 문제 푸는 과정을 1단계, 2단계... 식으로 {a_lang}로 아주 친절하게 설명하고 최종 정답 제시]
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.session_state['generated_qna'] = response.text
                except Exception as e:
                    st.error(f"문제 생성 중 에러가 발생했습니다: {e}")

    # 3. 생성된 문제와 해설을 화면에 예쁘게 출력하기
    if 'generated_qna' in st.session_state:
        st.divider()
        full_text = st.session_state['generated_qna']
        
        if "---" in full_text:
            question_part, answer_part = full_text.split("---", 1)
            
            st.markdown(question_part)
            
            with st.expander("👀 다 풀었나요? 정답 및 해설 확인하기 (클릭)"):
                st.markdown(answer_part)
        else:
            st.markdown(full_text)