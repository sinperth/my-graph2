
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.write(
    "1년간 박스오피스 10위권에 든 영화들의 "
    "장르, 관객 수, 개봉 정보 등을 살펴봅니다."
)

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/"
    "kobis_movies.csv"
)


@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일: 여덟 자리 숫자를 날짜로 변환
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 숫자형 열 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # 장르: 세로막대(|)가 있으면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("알 수 없음")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 빈 장르 처리
    df.loc[
        df["genre"].isin(["", "nan"]),
        "genre"
    ] = "알 수 없음"

    return df


try:
    df = load_data()

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.exception(e)
    st.stop()


# --------------------------------------------------
# 데이터 개요
# --------------------------------------------------

st.header("데이터 개요")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("전체 영화 편수", f"{len(df):,}편")

with col2:
    st.metric("장르 종류", f"{df['genre'].nunique():,}개")

with col3:
    st.metric("데이터 열 개수", f"{len(df.columns):,}개")


st.divider()


# ==================================================
# 그래프 1. 장르별 영화 편수
# ==================================================

st.header("그래프 1. 장르별 영화 편수")
st.subheader("어떤 장르의 영화가 가장 많을까?")

# 장르별 영화 편수 계산
genre_counts = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_counts.columns = ["장르", "영화 편수"]

# 도넛 그래프
fig = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.45,
    title="장르별 영화 편수"
)

fig.update_traces(
    textinfo="label+percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    ),
    textposition="outside"
)

fig.update_layout(
    height=550,
    legend_title="장르",
    margin=dict(t=70, b=30, l=30, r=30)
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# 그래프 설명 자리
st.markdown("### 이 그래프로 알 수 있는 것")
st.info(
    "장르별 영화 편수의 분포와 가장 많은 장르를 알 수 있습니다."
)

st.text_area(
    "그래프 해석 메모",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 적어 보세요.",
    key="graph1_memo",
    height=80
)


st.divider()


# --------------------------------------------------
# 다음 그래프를 추가할 자리
# --------------------------------------------------

st.header("다음 그래프")
st.write(
    "앞으로 영화 관객 수의 분포, 개봉일 스크린수와 관객 수의 관계 등 "
    "새로운 그래프를 이곳에 추가할 수 있습니다."
)
