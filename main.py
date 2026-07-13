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




import streamlit as st
import pandas as pd

st.set_page_config(page_title="서울-양평 열섬현상 & 전력수요 분석", layout="wide")

st.title("🌡️ 서울-양평 열섬현상 & 전력수요 분석")
st.caption("2025년 시간별 기온 및 전력수요 데이터를 바탕으로 분석합니다.")


# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yp = pd.read_csv("양평_기온.csv", encoding="cp949")
    power = pd.read_csv("전력수요.csv", encoding="cp949")

    seoul["일시"] = pd.to_datetime(seoul["일시"])
    yp["일시"] = pd.to_datetime(yp["일시"])
    power["일시"] = pd.to_datetime(power["일시"])

    # 열섬 분석용: 서울/양평 기온을 일시 기준으로 병합
    heat_df = pd.merge(
        seoul[["일시", "기온(°C)"]].rename(columns={"기온(°C)": "서울_기온"}),
        yp[["일시", "기온(°C)"]].rename(columns={"기온(°C)": "양평_기온"}),
        on="일시",
        how="inner",
    )
    heat_df["시각"] = heat_df["일시"].dt.hour
    heat_df["월"] = heat_df["일시"].dt.month

    # 전력 분석용: 서울 기온과 전력수요를 일시 기준으로 병합
    power_df = pd.merge(
        seoul[["일시", "기온(°C)"]].rename(columns={"기온(°C)": "서울_기온"}),
        power[["일시", "전력수요(MWh)"]],
        on="일시",
        how="inner",
    )
    power_df["월"] = power_df["일시"].dt.month

    return heat_df, power_df


try:
    heat_df, power_df = load_data()
except FileNotFoundError as e:
    st.error(
        "CSV 파일을 찾을 수 없습니다. '서울_기온.csv', '양평_기온.csv', '전력수요.csv' 파일이 "
        "app.py와 같은 폴더에 있는지 확인해주세요.\n\n"
        f"오류 내용: {e}"
    )
    st.stop()


tab1, tab2 = st.tabs(["🏙️ 열섬 분석", "⚡ 전력 연결"])


# =========================================================
# 탭1: 열섬 분석
# =========================================================
with tab1:
    st.header("① 1년간 기온 변화")
    line_df = heat_df.set_index("일시")[["서울_기온", "양평_기온"]]
    st.line_chart(line_df)

    st.header("② 시각별 평균 기온차 (서울 - 양평)")
    hour_group = heat_df.groupby("시각")[["서울_기온", "양평_기온"]].mean()
    hour_group["기온차(서울-양평)"] = hour_group["서울_기온"] - hour_group["양평_기온"]
    st.bar_chart(hour_group["기온차(서울-양평)"])

    with st.expander("시각별 평균 기온 데이터 보기"):
        st.dataframe(hour_group.round(2))

    st.header("③ 월별 평균 기온차 (서울 - 양평)")
    month_group = heat_df.groupby("월")[["서울_기온", "양평_기온"]].mean()
    month_group["기온차(서울-양평)"] = month_group["서울_기온"] - month_group["양평_기온"]
    st.bar_chart(month_group["기온차(서울-양평)"])

    with st.expander("월별 평균 기온 데이터 보기"):
        st.dataframe(month_group.round(2))

    st.subheader("📊 요약")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("서울 연평균 기온", f"{heat_df['서울_기온'].mean():.2f} °C")
    with col2:
        st.metric("양평 연평균 기온", f"{heat_df['양평_기온'].mean():.2f} °C")
    with col3:
        diff = heat_df["서울_기온"].mean() - heat_df["양평_기온"].mean()
        st.metric("연평균 기온차 (서울-양평)", f"{diff:.2f} °C")


# =========================================================
# 탭2: 전력 연결
# =========================================================
with tab2:
    st.header("① 기온과 전력수요의 관계")
    st.scatter_chart(power_df, x="서울_기온", y="전력수요(MWh)")

    st.header("② 기온 구간별 평균 전력수요")

    min_t = power_df["서울_기온"].min()
    max_t = power_df["서울_기온"].max()
    bins = list(range(int(min_t // 5 * 5), int(max_t // 5 * 5) + 10, 5))
    labels = [f"{b}~{b+5}°C" for b in bins[:-1]]

    power_df["기온구간"] = pd.cut(power_df["서울_기온"], bins=bins, labels=labels, right=False)
    bin_group = power_df.groupby("기온구간", observed=True)["전력수요(MWh)"].mean()
    st.bar_chart(bin_group)

    with st.expander("기온 구간별 평균 전력수요 데이터 보기"):
        st.dataframe(bin_group.round(1))

    st.header("③ 월별 평균 전력수요")
    month_power = power_df.groupby("월")["전력수요(MWh)"].mean()
    st.bar_chart(month_power)

    with st.expander("월별 평균 전력수요 데이터 보기"):
        st.dataframe(month_power.round(1))

    st.subheader("📊 요약")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("연평균 전력수요", f"{power_df['전력수요(MWh)'].mean():,.0f} MWh")
    with col2:
        corr = power_df["서울_기온"].corr(power_df["전력수요(MWh)"])
        st.metric("기온-전력수요 상관계수", f"{corr:.2f}")
