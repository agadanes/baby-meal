import streamlit as st
import random
import time

# --- 앱 설정 및 스타일 ---
st.set_page_config(page_title="유아식 매니저", layout="centered")
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%; height: 70px; font-size: 18px !important;
        font-weight: bold; margin-bottom: 10px; border-radius: 12px;
    }
    .recipe-card {
        padding: 15px; border-radius: 10px; background-color: #f0f2f6; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 데이터 저장소 (세션 상태) ---
if 'recipe_db' not in st.session_state:
    # 기본 샘플 데이터 (테스트용)
    st.session_state.recipe_db = [
        {"title": "한우 팝콘", "ingredients": "소고기 다짐육", "tag": "소고기"},
        {"title": "닭안심 감자볶음", "ingredients": "닭안심, 감자", "tag": "단백질"},
        {"title": "대구살 채소 진밥", "ingredients": "대구살, 당근", "tag": "생선"}
    ]
if 'page' not in st.session_state:
    st.session_state.page = "main"

# --- [메인 기능 1] 식단 짜기 로직 (방법 A) ---
def generate_plan(days=1):
    plans = []
    for i in range(days):
        # 규칙: 하루 한 끼는 무조건 '소고기' 포함
        beef_recipes = [r for r in st.session_state.recipe_db if "소고기" in r['tag'] or "한우" in r['title']]
        other_recipes = [r for r in st.session_state.recipe_db if r not in beef_recipes]
        
        day_menu = {
            "아침": random.choice(st.session_state.recipe_db)['title'],
            "점심": random.choice(beef_recipes)['title'] if beef_recipes else "레시피 부족",
            "저녁": random.choice(other_recipes)['title'] if other_recipes else "레시피 부족"
        }
        plans.append(day_menu)
    return plans

# --- 화면 전환 로직 ---
if st.session_state.page == "main":
    st.title("👶 유아식 식단 도우미")
    
    if st.button("📸 새 레시피 등록 (사진/링크)"):
        st.session_state.page = "add"
        st.rerun()
        
    if st.button("📅 오늘 식단 짜기"):
        st.session_state.page = "plan_1"
        st.rerun()
        
    if st.button("🗓️ 3일치 식단 한꺼번에 짜기"):
        st.session_state.page = "plan_3"
        st.rerun()

# --- [메인 기능 2] 레시피 등록 및 유튜브 추출 (방법 B) ---
elif st.session_state.page == "add":
    st.header("📝 레시피 추가")
    
    # 사진 업로드 (OCR)
    img = st.file_uploader("사진 올리기", type=['jpg', 'png'])
    # 유튜브 링크 추출
    yt_link = st.text_input("유튜브 또는 블로그 링크 붙여넣기")
    
    if yt_link or img:
        with st.status("AI가 레시피 분석 중...", expanded=True):
            time.sleep(2)
            # 분석 결과 시뮬레이션
            new_title = "추출된 메뉴 이름"
            new_ing = "추출된 재료 정보"
            st.write("✅ 분석 완료!")
        
        title = st.text_input("메뉴 이름 수정", value=new_title)
        ing = st.text_area("재료 수정", value=new_ing)
        tag = st.selectbox("핵심 재료 태그", ["소고기", "단백질", "채소", "기타"])
        
        if st.button("내 창고에 저장"):
            st.session_state.recipe_db.append({"title": title, "ingredients": ing, "tag": tag})
            st.success("저장되었습니다!")
            st.session_state.page = "main"
            st.rerun()

    if st.button("🔙 돌아가기"):
        st.session_state.page = "main"
        st.rerun()

# --- 식단 결과 화면 ---
elif st.session_state.page in ["plan_1", "plan_3"]:
    days = 1 if st.session_state.page == "plan_1" else 3
    st.header(f"🗓️ {days}일 식단 계획")
    
    plans = generate_plan(days)
    for idx, day in enumerate(plans):
        with st.container():
            st.subheader(f"Day {idx+1}")
            st.markdown(f"""
            <div class="recipe-card">
                🌅 <b>아침</b>: {day['아침']}<br>
                ☀️ <b>점심</b>: {day['점심']} (철분 강화)<br>
                🌙 <b>저녁</b>: {day['저녁']}
            </div>
            """, unsafe_allow_html=True)

    if st.button("🔙 홈으로 돌아가기"):
        st.session_state.page = "main"
        st.rerun()
