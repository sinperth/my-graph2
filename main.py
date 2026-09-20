
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

    # 장르: | 기호가 있으면 첫 번째 장르만 사용
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

genre_counts = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_counts.columns = ["장르", "영화 편수"]

fig1 = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.45,
    title="장르별 영화 편수"
)

fig1.update_traces(
    textinfo="label+percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    ),
    textposition="outside"
)

fig1.update_layout(
    height=550,
    legend_title="장르",
    margin=dict(t=70, b=30, l=30, r=30)
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.markdown("### 이 그래프로 알 수 있는 것")

st.info(
    "10위권에 든 영화의 장르 구성에는"
    "애니메이션,드라마,공포(호러),액션,"
    "공연,코미디,스릴러,범죄,다큐멘터리,SF"
    "가 있다"  
)

st.text_area(
    "그래프 1 해석 메모",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 적어 보세요.",
    key="graph1_memo",
    height=80
)


st.divider()


# ==================================================
# 그래프 2. 장르별 영화 트리맵
# ==================================================

st.header("그래프 2. 장르별 영화 트리맵")
st.subheader("어떤 장르에 관객이 많이 몰려 있을까?")

st.write(
    "장르 안에 영화가 들어 있습니다. "
    "칸의 크기는 총 관객 수를 나타냅니다."
)

treemap_df = df[
    ["genre", "movieNm", "total_audi"]
].copy()

treemap_df = treemap_df.dropna(
    subset=["movieNm", "total_audi"]
)

treemap_df = treemap_df[
    treemap_df["total_audi"] >= 0
]

treemap_df = treemap_df[
    treemap_df["movieNm"].astype(str).str.strip() != ""
]

fig2 = px.treemap(
    treemap_df,
    path=["genre", "movieNm"],
    values="total_audi",
    color="genre",
    title="장르별 영화 총 관객 트리맵",
    custom_data=["movieNm", "total_audi"]
)

fig2.update_traces(
    hovertemplate=(
        "<b>영화명: %{customdata[0]}</b><br>"
        "총 관객: %{customdata[1]:,}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    height=700,
    margin=dict(t=70, b=30, l=10, r=10)
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.markdown("### 이 그래프로 알 수 있는 것")

st.info(
    "애니메이션에서는 주토피아2" 
    "사극에서는 왕과 사는 남자"
    "SF에서는 아바타: 불과 재"
    "액션/드라마/어드벤처에서는 오디세이"
    "액션에서는 군체"
    "공포(호러)에서는 살목지"
    "스릴러에서는 어쩔 수가 없다"
    "각 장르마다 큰 영화가 있다."
)

st.text_area(
    "그래프 2 해석 메모",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 적어 보세요.",
    key="graph2_memo",
    height=80
)


st.divider()


# ==================================================
# 그래프 3. 총 관객 수 히스토그램
# ==================================================

st.header("그래프 3. 총 관객 수 히스토그램")
st.subheader("영화들의 총 관객 수는 어느 구간에 몰려 있을까?")

st.write(
    "가로축은 영화의 총 관객 수, "
    "세로축은 해당 구간에 속한 영화 편수입니다."
)

hist_df = df[
    ["movieNm", "total_audi"]
].copy()

hist_df = hist_df.dropna(
    subset=["movieNm", "total_audi"]
)

hist_df = hist_df[
    hist_df["total_audi"] >= 0
]

fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 수 분포",
    labels={
        "total_audi": "총 관객 수",
        "count": "영화 편수"
    }
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

fig3.update_layout(
    height=550,
    bargap=0.05,
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수",
    margin=dict(t=70, b=70, l=50, r=30)
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# 대부분의 영화가 몰려 있는 구간 계산
if len(hist_df) > 0:

    counts, bin_edges = pd.cut(
        hist_df["total_audi"],
        bins=20,
        include_lowest=True,
        retbins=True
    )

    bin_counts = counts.value_counts().sort_index()

    most_common_bin = bin_counts.idxmax()
    most_common_count = bin_counts.max()

    lower_bound = most_common_bin.left
    upper_bound = most_common_bin.right

    max_audience = hist_df["total_audi"].max()

    top_movies = hist_df[
        hist_df["total_audi"] == max_audience
    ]

    top_movie_names = top_movies["movieNm"].tolist()

    top_movie_text = ", ".join(top_movie_names)

    st.markdown("### 이 그래프로 알 수 있는 것")

    st.info(
        f"대부분의 영화는 총 관객 "
        f"0명 이상 "
        f"99 만 명 이하 구간에 몰려 있습니다. "
        f"이 구간에는 207편의 영화가 있습니다."
    )

    st.success(
        f"총 관객이 가장 많은 영화는 "
        f"**{top_movie_text}**이며, "
        f"총 관객은 **{max_audience:,.0f}명**입니다."
    )

else:

    st.warning(
        "총 관객 수 데이터가 없어 분포를 계산할 수 없습니다."
    )

st.text_area(
    "그래프 3 해석 메모",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 적어 보세요.",
    key="graph3_memo",
    height=80
)


st.divider()


# ==================================================
# 그래프 4. 개봉일 스크린수와 총 관객의 관계
# ==================================================

st.header("그래프 4. 개봉일 스크린수와 총 관객의 관계")
st.subheader("개봉일 스크린수가 많으면 총 관객도 많을까?")

st.write(
    "영화마다 개봉일 스크린수와 총 관객 수를 점으로 표시합니다. "
    "장르별로 점 색을 다르게 했습니다."
)

scatter_df = df[
    ["movieNm", "genre", "first_scrn", "total_audi"]
].copy()

scatter_df = scatter_df.dropna(
    subset=[
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi"
    ]
)

scatter_df = scatter_df[
    (scatter_df["first_scrn"] >= 0)
    & (scatter_df["total_audi"] >= 0)
]

fig4 = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객 수",
        "genre": "장르"
    },
    custom_data=["movieNm", "genre"]
)

fig4.update_traces(
    hovertemplate=(
        "<b>영화명: %{customdata[0]}</b><br>"
        "장르: %{customdata[1]}<br>"
        "개봉일 스크린수: %{x:,}개<br>"
        "총 관객: %{y:,}명"
        "<extra></extra>"
    ),
    marker=dict(
        size=10,
        opacity=0.75
    )
)

fig4.update_layout(
    height=650,
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title="장르",
    margin=dict(t=70, b=70, l=60, r=30)
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.markdown("### 이 그래프로 알 수 있는 것")

st.info(
    "스크린 수가 많을수록 총관객수도 많다"
)

st.text_area(
    "그래프 4 해석 메모",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 적어 보세요.",
    key="graph4_memo",
    height=80
)


st.divider()


# ==================================================
# 그래프 5. 장르별 총 관객 상자 그림
# ==================================================

st.header("그래프 5. 장르별 총 관객 상자 그림")
st.subheader("장르별 총 관객 수의 분포는 어떻게 다를까?")

st.write(
    "영화가 10편 이상인 장르만 골라 비교합니다. "
    "상자 밖으로 튀어나온 점은 해당 장르의 다른 영화들과 비교해 "
    "상대적으로 멀리 떨어진 관측값입니다."
)

# 박스플롯에 사용할 데이터
box_df = df[
    ["genre", "movieNm", "total_audi"]
].copy()

box_df = box_df.dropna(
    subset=["genre", "movieNm", "total_audi"]
)

box_df = box_df[
    box_df["total_audi"] >= 0
]

# 영화가 10편 이상인 장르만 선택
genre_movie_counts = (
    box_df["genre"]
    .value_counts()
)

valid_genres = genre_movie_counts[
    genre_movie_counts >= 10
].index

box_df = box_df[
    box_df["genre"].isin(valid_genres)
]

# 박스플롯
fig5 = px.box(
    box_df,
    x="genre",
    y="total_audi",
    color="genre",
    points="outliers",
    title="영화가 10편 이상인 장르별 총 관객 분포",
    labels={
        "genre": "장르",
        "total_audi": "총 관객 수"
    },
    custom_data=["movieNm", "genre"]
)

# 상자 밖 이상치에 마우스를 올렸을 때 영화명 표시
fig5.update_traces(
    hovertemplate=(
        "<b>영화명: %{customdata[0]}</b><br>"
        "장르: %{customdata[1]}<br>"
        "총 관객: %{y:,}명"
        "<extra></extra>"
    ),
    marker=dict(
        size=9,
        opacity=0.8
    )
)

fig5.update_layout(
    height=650,
    showlegend=False,
    xaxis_title="장르",
    yaxis_title="총 관객 수",
    margin=dict(t=70, b=70, l=60, r=30)
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.markdown("### 이 그래프로 알 수 있는 것")

st.info(
    "장르에따라 영화들을 비교하는데"
    "다른 영화들과 비교해 상대적으로"
    "멀리 떨어진 영화들은 점으로 분포된다"
)

st.text_area(
    "그래프 5 해석 메모",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 적어 보세요.",
    key="graph5_memo",
    height=80
)


st.divider()


# --------------------------------------------------
# 다음 그래프를 추가할 자리
# --------------------------------------------------

st.header("다음 그래프")

st.write(
    "앞으로 영화 관객 수의 분포, 개봉일 상영횟수와 관객 수의 관계 등 "
    "새로운 그래프를 이곳에 추가할 수 있습니다."
)

# ==================================================
# 그래프 6. 첫 주 관객을 크기로 나타낸 버블 그래프
# ==================================================

st.header("그래프 6. 첫 주 관객을 크기로 나타낸 버블 그래프")
st.subheader("첫 주 관객이 많은 영화는 어떤 위치에 있을까?")

st.write(
    "가로축은 개봉일 스크린수, 세로축은 총 관객 수입니다. "
    "버블의 크기는 개봉 첫 주 관객 수를 나타내며, 장르별로 색을 다르게 했습니다."
)

# 버블 그래프에 사용할 데이터
bubble_df = df[
    [
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
].copy()

bubble_df = bubble_df.dropna(
    subset=[
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi",
        "first_week_audi"
    ]
)

# 음수 데이터 제외
bubble_df = bubble_df[
    (bubble_df["first_scrn"] >= 0)
    & (bubble_df["total_audi"] >= 0)
    & (bubble_df["first_week_audi"] >= 0)
]

# 버블 그래프
fig6 = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객의 관계 - 첫 주 관객 버블",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객 수",
        "first_week_audi": "개봉 첫 주 관객",
        "genre": "장르"
    },
    custom_data=[
        "movieNm",
        "genre",
        "first_week_audi"
    ],
    size_max=60
)

# 마우스를 올렸을 때 표시할 내용
fig6.update_traces(
    hovertemplate=(
        "<b>영화명: %{customdata[0]}</b><br>"
        "장르: %{customdata[1]}<br>"
        "개봉일 스크린수: %{x:,}개<br>"
        "총 관객: %{y:,}명<br>"
        "개봉 첫 주 관객: %{customdata[2]:,}명"
        "<extra></extra>"
    ),
    marker=dict(
        opacity=0.7,
        line=dict(width=1)
    )
)

fig6.update_layout(
    height=700,
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객 수",
    legend_title="장르",
    margin=dict(t=70, b=70, l=60, r=30)
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

st.markdown("### 이 그래프로 알 수 있는 것")

st.info(
    "개봉일 스크린수와 총 관객 수의 관계를 보면서 "
    "개봉 첫 주 관객이 많은 영화가 버블의 크기로 어떻게 나타나는지 비교할 수 있습니다."
)

st.text_area(
    "그래프 6 해석 메모",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 적어 보세요.",
    key="graph6_memo",
    height=80
)

st.divider()

# ==================================================
# 그래프 7. 제작 국가 → 장르 선버스트
# ==================================================

st.header("그래프 7. 제작 국가에서 장르로 내려가는 선버스트")
st.subheader("어떤 나라에서 어떤 장르의 영화가 많이 만들어졌을까?")

st.write(
    "바깥쪽으로 갈수록 세부 장르를 나타냅니다. "
    "각 칸의 크기는 해당 제작 국가와 장르에 속하는 영화 편수를 나타냅니다."
)

sunburst_df = df[
    ["nation", "genre", "movieNm"]
].copy()

sunburst_df = sunburst_df.dropna(
    subset=["nation", "genre", "movieNm"]
)

sunburst_df["nation"] = sunburst_df["nation"].astype(str).str.strip()
sunburst_df["genre"] = sunburst_df["genre"].astype(str).str.strip()
sunburst_df["movieNm"] = sunburst_df["movieNm"].astype(str).str.strip()

sunburst_df = sunburst_df[
    (sunburst_df["nation"] != "")
    & (sunburst_df["genre"] != "")
    & (sunburst_df["movieNm"] != "")
    & (sunburst_df["nation"].str.lower() != "nan")
    & (sunburst_df["genre"].str.lower() != "nan")
]

# 제작 국가 × 장르별 영화 편수 계산
sunburst_counts = (
    sunburst_df
    .groupby(["nation", "genre"])
    .size()
    .reset_index(name="영화 편수")
)

fig7 = px.sunburst(
    sunburst_counts,
    path=["nation", "genre"],
    values="영화 편수",
    title="제작 국가 → 장르별 영화 편수",
    custom_data=["영화 편수"]
)

fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편"
        "<extra></extra>"
    )
)

fig7.update_layout(
    height=700,
    margin=dict(t=70, b=40, l=30, r=30)
)

st.plotly_chart(
    fig7,
    use_container_width=True
)

st.markdown("### 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프 7 해석 메모",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 적어 보세요.",
    key="graph7_memo",
    height=80
)

st.divider()

# ==================================================
# 그래프 8. 개봉 첫 주 관객이 많으면 총 관객수도 많을까?
# ==================================================

st.header("그래프 8. 개봉 첫 주 관객이 많으면 총 관객수도 많을까?")

st.write(
    "가로축은 개봉 첫 주 관객, 세로축은 총 관객 수입니다. "
    "각 점에 마우스를 올리면 영화명을 확인할 수 있습니다."
)

scatter8_df = df[
    [
        "movieNm",
        "first_week_audi",
        "total_audi"
    ]
].copy()

scatter8_df = scatter8_df.dropna(
    subset=[
        "movieNm",
        "first_week_audi",
        "total_audi"
    ]
)

scatter8_df = scatter8_df[
    (scatter8_df["movieNm"].astype(str).str.strip() != "")
    & (scatter8_df["first_week_audi"] >= 0)
    & (scatter8_df["total_audi"] >= 0)
]

fig8 = px.scatter(
    scatter8_df,
    x="first_week_audi",
    y="total_audi",
    hover_name="movieNm",
    title="개봉 첫 주 관객이 많으면 총 관객수도 많을까?",
    labels={
        "first_week_audi": "개봉 첫 주 관객",
        "total_audi": "총 관객 수"
    }
)

fig8.update_traces(
    marker=dict(
        size=10,
        opacity=0.75
    ),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉 첫 주 관객: %{x:,}명<br>"
        "총 관객: %{y:,}명"
        "<extra></extra>"
    )
)

fig8.update_layout(
    height=650,
    xaxis_title="개봉 첫 주 관객",
    yaxis_title="총 관객 수",
    margin=dict(t=70, b=70, l=60, r=30)
)

st.plotly_chart(
    fig8,
    use_container_width=True
)

st.markdown("### 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프 8 해석 메모",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 적어 보세요.",
    key="graph8_memo",
    height=80
)

st.divider()
