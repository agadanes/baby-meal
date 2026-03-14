import streamlit as st
import pandas as pd
import os
import random
import time
from PIL import Image
import easyocr
import numpy as np
import re

# --- 앱 설정 ---
st.set_page_config(page_title="똑똑 유아식 매니저", layout="centered")

# --- 데이터 파일 경로 ---
DB_FILE = "recipes.csv"

# --- 데이터 저장/불러오기 함수 ---
def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE).to_dict('records')
        except:
            return []
    return []

def save_data(data):
    pd.DataFrame(data).to_csv(DB_FILE, index=False)

# --- 초기 데이터 로드 ---
if 'recipe_db' not in st.session_state:
    st.session_state.recipe_db = load_data()
if 'page' not in st.session_state: 
    st.session_state.page = "main"

# --- 스타일 설정 ---
st.markdown("""
    <style>
    div.stButton > button { width: 100%; height: 60px; font-size: 18px !important; font-weight: bold; border-radius: 12px; margin-bottom: 10px; }
    .recipe-card { padding: 20px; border-radius: 15px; background-color: #ffffff; border: 1px solid #e0e0e0; margin-bottom: 15px; box-shadow: 2px 4px 10px rgba(0,0,0,0.05); }
    .meal-tag { background-color: #ffefef; color: #ff4b4b; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; font-weight: bold; }
    .ingredient-display { background-color: #f1f3f5; padding: 12px; border-radius: 8px; font-size: 0.95em; line-height: 1.8; white-space: pre-wrap; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 텍스트 정제 함수 ---
def smart_clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    keywords = ['재료', '방법', '만드는 법', '준비물', '순서']
    for k in keywords:
        text = text.replace(k, f"\n\n[{k}]\n")
    text = re.sub(r'(\d+\s?[gGmlL]|[T|t]|스푼|알|개|컵|작은술|큰술)', r'\1\n', text)
    text = re.sub(r'(\d\.)', r'\n\1', text)
    return text.strip()

@st.cache_resource
def get_reader():
    return easyocr.Reader(['ko', 'en'])

# --- [페이지 1] 메인 화면 ---
if st.session_state.page == "main":
    st.title("👶 아이 식단 매니저")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📸 레시피 등록"): st.session_state.page = "add"; st.rerun()
    with col2:
        if st.button("📂 레시피 창고"): st.session_state.page = "storage"; st.rerun()
    if st.button("📅 오늘 식단 짜기"): st.session_state.page = "plan_1"; st.rerun()
    if st.button("🗓️ 3일치 식단 짜기"): st.session_state.page = "plan_3"; st.rerun()

# --- [페이지 2] 레시피 등록 ---
elif st.session_state.page == "add":
    st.header("📝 레시피 정리하기")
    img_file = st.file_uploader("이미지 업로드", type=['jpg', 'png', 'jpeg'])
    
    if img_file:
        image = Image.open(img_file)
        st.image(image, use_container_width=True)
        if st.button("🔍 사진 분석해서 목록 만들기"):
            with st.spinner("분석 중..."):
                reader = get_reader()
                result = reader.readtext(np.array(image), detail=0)
                st.session_state.temp_ing = smart_clean_text(" ".join(result))
                st.success("분석 완료!")

    title = st.text_input("🍴 메뉴 이름")
    ing = st.text_area("🛒 내용 정리", value=st.session_state.get('temp_ing', ''), height=250)
    
    # 요청하신 대로 분류 수정
    tag = st.selectbox("핵심 분류", ["소고기 (30g 필수)", "닭고기", "돼지고기", "채소", "기타"])
    
    if st.button("✅ 이대로 창고에 저장"):
        st.session_state.recipe_db.append({"title": title, "content": ing, "tag": tag})
        save_data(st.session_state.recipe_db)
        st.success("데이터가 안전하게 저장되었습니다.")
        time.sleep(1)
        st.session_state.page = "main"; st.rerun()
    
    if st.button("🔙 돌아가기"): st.session_state.page = "main"; st.rerun()

# --- [페이지 3] 레시피 창고 ---
elif st.session_state.page == "storage":
    st.header("📂 레시피 창고")
    if not st.session_state.recipe_db:
        st.write("저장된 레시피가 없어요.")
    else:
        for idx, r in enumerate(st.session_state.recipe_db):
            with st.expander(f"🍴 {r['title']} ({r['tag']})"):
                st.markdown(f"<div class='ingredient-display'>{r['content']}</div>", unsafe_allow_html=True)
                if st.button(f"삭제하기", key=f"del_{idx}"):
                    st.session_state.recipe_db.pop(idx)
                    save_data(st.session_state.recipe_db)
                    st.rerun()
    if st.button("🔙 메인"): st.session_state.page = "main"; st.rerun()

# --- [페이지 4] 식단 결과 ---
elif st.session_state.page in ["plan_1", "plan_3"]:
    days = 1 if st.session_state.page == "plan_1" else 3
    st.header(f"🗓️ {days}일 권장 식단")
    
    # 소고기 메뉴 필터링 로직
    beef_recipes = [r for r in st.session_state.recipe_db if "소고기" in str(r['tag'])]
    other_recipes = [r for r in st.session_state.recipe_db if "소고기" not in str(r['tag'])]

    if not beef_recipes:
        st.error("❗ 소고기 레시피가 최소 1개는 있어야 식단을 짤 수 있어요.")
    elif len(st.session_state.recipe_db) < 3:
        st.warning("⚠️ 식단 구성을 위해 레시피를 더 등록해주세요 (최소 3개 이상)")
    else:
        for i in range(days):
            day_beef = random.choice(beef_recipes)
            # 아침, 저녁은 소고기 제외한 메뉴 중 랜덤 선택 (중복 방지)
            day_others = random.sample(other_recipes, 2) if len(other_recipes) >= 2 else other_recipes
            
            st.markdown(f"""
            <div class="recipe-card">
                <h3>📅 Day {i+1}</h3>
                <p>🌅 아침: <b>{day_others[0]['title'] if len(day_others)>0 else '메뉴 부족'}</b></p>
                <p>☀️ 점심(필수): <b>{day_beef['title']}</b> <span class="meal-tag">소고기 30g</span></p>
                <p>🌙 저녁: <b>{day_others[1]['title'] if len(day_others)>1 else '메뉴 부족'}</b></p>
            </div>
            """, unsafe_allow_html=True)
    if st.button("🔙 홈"): st.session_state.page = "main"; st.rerun()
