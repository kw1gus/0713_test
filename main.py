import streamlit as st
import pandas as pd

st.set_page_config(page_title="서울-양평 도시 열섬현상 분석", layout="wide")

st.title("🌡️ 서울-양평 도시 열섬현상 분석")
st.caption("2025년 시간별 기온 데이터를 바탕으로 서울과 양평의 기온 차이를 살펴봅니다.")


# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yp = pd.read_csv("양평_기온.csv", encoding="cp949")

    seoul["지역"] = "서울"
    yp["지역"] = "양평"

    df = pd.concat([seoul, yp], ignore_index=True)
    df["일시"] = pd.to_datetime(df["일시"])
    df["시각"] = df["일시"].dt.hour
    df["월"] = df["일시"].dt.month

    return df


try:
    df = load_data()
except FileNotFoundError as e:
    st.error(
        "CSV 파일을 찾을 수 없습니다. '서울_기온.csv'와 '양평_기온.csv' 파일이 "
        "app.py와 같은 폴더에 있는지 확인해주세요.\n\n"
        f"오류 내용: {e}"
    )
    st.stop()


# -----------------------------
# ① 1년간 두 지역의 기온 변화 (선그래프)
# -----------------------------
st.header("① 1년간 기온 변화")

line_df = df.pivot_table(index="일시", columns="지역", values="기온(°C)")
st.line_chart(line_df)


# -----------------------------
# ② 시각(0~23시)별 평균 기온차, 서울-양평 (막대그래프)
# -----------------------------
st.header("② 시각별 평균 기온차 (서울 - 양평)")

hour_pivot = df.pivot_table(index="시각", columns="지역", values="기온(°C)", aggfunc="mean")
hour_pivot["기온차(서울-양평)"] = hour_pivot["서울"] - hour_pivot["양평"]

st.bar_chart(hour_pivot["기온차(서울-양평)"])

with st.expander("시각별 평균 기온 데이터 보기"):
    st.dataframe(hour_pivot.round(2))


# -----------------------------
# ③ 월(1~12월)별 평균 기온차, 서울-양평 (막대그래프)
# -----------------------------
st.header("③ 월별 평균 기온차 (서울 - 양평)")

month_pivot = df.pivot_table(index="월", columns="지역", values="기온(°C)", aggfunc="mean")
month_pivot["기온차(서울-양평)"] = month_pivot["서울"] - month_pivot["양평"]

st.bar_chart(month_pivot["기온차(서울-양평)"])

with st.expander("월별 평균 기온 데이터 보기"):
    st.dataframe(month_pivot.round(2))


# -----------------------------
# 요약 통계
# -----------------------------
st.header("📊 요약")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("서울 연평균 기온", f"{df[df['지역']=='서울']['기온(°C)'].mean():.2f} °C")
with col2:
    st.metric("양평 연평균 기온", f"{df[df['지역']=='양평']['기온(°C)'].mean():.2f} °C")
with col3:
    diff = df[df['지역']=='서울']['기온(°C)'].mean() - df[df['지역']=='양평']['기온(°C)'].mean()
    st.metric("연평균 기온차 (서울-양평)", f"{diff:.2f} °C")
