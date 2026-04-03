import streamlit as st
import PyPDF2
import google.generativeai as genai

# --- ✨ 앱 기본 설정 ---
st.set_page_config(page_title="나만의 AI 전담 조교", page_icon="👨‍🏫", layout="centered")

# --- 🔑 Gemini AI 설정 (기존 secrets.toml 활용) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3-flash-preview')
except Exception as e:
    st.error("API 키 설정에 문제가 있습니다. secrets.toml 파일을 확인해주세요.")

# --- 🖥️ 메인 화면 ---
st.title("📚 스마트 PDF 과제 분석기")
st.write("복잡한 강의 계획서나 과제(Lab) 매뉴얼 PDF를 올려주세요. A+를 위한 핵심만 짚어드립니다!")

# 1. 파일 업로드 버튼
uploaded_file = st.file_uploader("여기에 PDF 파일을 드래그 앤 드롭 하세요", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("👀 AI 조교가 PDF 문서를 열심히 읽고 있습니다... ⏳"):
        try:
            # 2. PDF 파일에서 텍스트만 쏙쏙 뽑아내기
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            document_text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    document_text += extracted
                    
            st.success("문서 읽기 완료! 이제 과제 분석을 시작할 수 있습니다.")
            
            with st.expander("📄 추출된 원본 텍스트 슬쩍 보기"):
                st.text(document_text[:1000] + "\n\n... (중략) ...")

            st.divider()

            # 3. AI에게 분석 명령 내리기 (프롬프트 엔지니어링)
            if st.button("🚀 AI 조교에게 A+ 공략법 물어보기", use_container_width=True, type="primary"):
                with st.spinner("🤔 문서의 행간을 읽으며 감점 포인트를 찾는 중입니다... ✍️"):
                    prompt = f"""
                    너는 대학교의 깐깐하지만 학생을 진심으로 아끼는 A+ 전담 조교(TA)야.
                    다음은 학생이 업로드한 과제 설명서(또는 강의 계획서) PDF의 텍스트야.

                    [문서 내용 시작]
                    {document_text}
                    [문서 내용 끝]

                    이 문서를 꼼꼼하게 분석해서, 학생이 만점을 받기 위해 반드시 알아야 할 내용들을 아래 양식에 맞춰서 한국어로 아주 명확하게 정리해 줘. 
                    (마크다운을 사용해서 가독성 좋게 꾸며줘.)

                    1. 🚨 **핵심 데드라인 및 제출 규칙:** (언제까지, 어떤 파일 형식이나 방식으로 제출해야 하는지)
                    2. ✅ **필수 요구사항 (Must-do):** (교수님이 절대 빠뜨리지 말라고 강조한 핵심 조건 3~5가지)
                    3. ⚠️ **감점 주의사항 (Pitfalls):** (학생들이 흔히 실수해서 점수를 깎이는 치명적인 부분)
                    4. 💡 **A+ 공략 꿀팁:** (이 과제의 숨겨진 의도나, 조교로서 조언해 주는 고득점 비법)
                    """
                    
                    response = model.generate_content(prompt)
                    
                    # 4. 결과 출력
                    st.markdown("### 👨‍🏫 AI 조교의 과제 분석 리포트")
                    st.info(response.text)
                    
        except Exception as e:
            st.error(f"파일을 읽거나 분석하는 중 오류가 발생했습니다: {e}")
