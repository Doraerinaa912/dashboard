import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="FEM Dashboard - ROA Analysis",
    page_icon="📊",
    layout="wide"
)
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# =====================================================
# LOAD DATA
# =====================================================

try:
    df = pd.read_excel("clean_data.xlsx")
except:
    st.warning("Không tìm thấy file clean_data.xlsx")
    df = None

# =====================================================
# MODEL RESULTS
# =====================================================

MODEL_NAME = "Fixed Effects Model (FEM)"

R2 = 0.6254
F_STAT = 2375.6
OBS = 7805
ENTITIES = 686

# Coefficients
coef_data = pd.DataFrame({
    "Variable": [
        "Pre-Tax Profit Margin",
        "Asset Turnover",
        "Net Profit Margin²",
        "Current Ratio",
        "DE × Current Ratio"
    ],
    "Coefficient": [
        0.2936,
        5.4445,
        0.0040,
        0.3634,
        -0.2363
    ],
    "LowerCI": [
        0.2861,
        5.0344,
        0.0036,
        0.2263,
        -0.2955
    ],
    "UpperCI": [
        0.3011,
        5.8546,
        0.0045,
        0.5005,
        -0.1771
    ]
})

# Diagnostics
DW = 0.8169
JB = 2993.7513
LM = 872.6890
MAX_VIF = 4.4545

# =====================================================
# TITLE
# =====================================================

st.title("📊 Dashboard Phân tích Kinh tế lượng")

st.markdown("""
<div class="center-subtitle">
Mô hình FEM dự báo ROA (Return On Assets)
</div>
""", unsafe_allow_html=True)



tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📌 Tổng quan mô hình",
        "📈 Tác động của từng biến",
        "⚠️ Phát hiện vi phạm",
        "🔮 Dự báo tương tác"
    ]
)

# =====================================================
# TAB 1
# =====================================================

with tab1:

    st.subheader("Tổng quan mô hình")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Model", "FEM")
    c2.metric("R²", f"{R2:.4f}")
    c3.metric("F-statistic", f"{F_STAT:.1f}")
    c4.metric("Observations", f"{OBS:,}")
    c5.metric("Entities", f"{ENTITIES}")

    st.markdown("---")

    st.info(
        """
        **Kết luận:**
        
        - Mô hình được lựa chọn: Fixed Effects Model (FEM)
        - R² = 62.54% cho thấy mô hình giải thích được phần lớn biến động của ROA.
        - Mô hình có ý nghĩa thống kê tổng thể (F-test p-value < 0.05).
        """
    )

# =====================================================
# TAB 2
# =====================================================

with tab2:

    st.subheader("Tác động của các biến đến ROA")

    plot_df = coef_data.sort_values(
        "Coefficient",
        ascending=True
    )

    colors = [
        "Positive" if x > 0 else "Negative"
        for x in plot_df["Coefficient"]
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=plot_df["Coefficient"],
            y=plot_df["Variable"],
            orientation="h",
            marker_color=[
                "green" if x > 0 else "red"
                for x in plot_df["Coefficient"]
            ],
            error_x=dict(
                type="data",
                symmetric=False,
                array=plot_df["UpperCI"] - plot_df["Coefficient"],
                arrayminus=plot_df["Coefficient"] - plot_df["LowerCI"]
            )
        )
    )

    fig.update_layout(
        title="Hệ số hồi quy và khoảng tin cậy 95%",
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.dataframe(
        coef_data,
        use_container_width=True
    )

# =====================================================
# TAB 3
# =====================================================

with tab3:

    st.subheader("Chẩn đoán mô hình")

    diagnostics = pd.DataFrame({
        "Kiểm định": [
            "Durbin-Watson",
            "Jarque-Bera",
            "LM Test",
            "Max VIF"
        ],
        "Giá trị": [
            DW,
            JB,
            LM,
            MAX_VIF
        ],
        "Trạng thái": [
            "🔴 Tự tương quan",
            "🔴 Không chuẩn",
            "🔴 Phương sai thay đổi",
            "🟢 Không đa cộng tuyến nghiêm trọng"
        ]
    })

    st.dataframe(
        diagnostics,
        use_container_width=True
    )

    st.markdown("### Đánh giá")

    st.error(
        """
        - Có dấu hiệu tự tương quan (DW = 0.8169)
        - Có phương sai sai số thay đổi
        - Phần dư không phân phối chuẩn
        """
    )

    st.success(
        """
        - Không phát hiện đa cộng tuyến nghiêm trọng
        - Max VIF = 4.45 (<10)
        """
    )

# =====================================================
# TAB 4
# =====================================================

with tab4:

    st.subheader("Dự báo ROA")

    col1, col2 = st.columns(2)

    with col1:

        ptpm = st.number_input(
            "Pre-Tax Profit Margin",
            value=10.0
        )

        asset_turnover = st.number_input(
            "Asset Turnover",
            value=1.0
        )

        npm = st.number_input(
            "Net Profit Margin",
            value=10.0
        )

    with col2:

        current_ratio = st.number_input(
            "Current Ratio",
            value=2.0
        )

        debt_equity = st.number_input(
            "Debt/Equity Ratio",
            value=1.0
        )

    npm_squared = npm ** 2

    de_interaction = (
        debt_equity *
        current_ratio
    )

    roa_pred = (
        -3.1840
        + 0.2936 * ptpm
        + 5.4445 * asset_turnover
        + 0.0040 * npm_squared
        + 0.3634 * current_ratio
        - 0.2363 * de_interaction
    )

    st.markdown("---")

    st.metric(
        "ROA dự báo (%)",
        f"{roa_pred:.2f}"
    )

    st.caption(
        "Dự báo dựa trên hệ số FEM đã lựa chọn."
    )

# =====================================================
# OPTIONAL DATA EXPLORATION
# =====================================================

if df is not None:

    st.markdown("---")
    st.subheader("📂 Dữ liệu sử dụng")

    st.write(df.head())

    st.write(
        f"Số dòng dữ liệu: {len(df):,}"
    )

# =====================================================
# HISTOGRAM
# =====================================================

if df is not None:

    fig = px.histogram(
        df,
        x="ROA - Return On Assets",
        nbins=40
    )

    fig.update_traces(
        marker_color="rgba(0,212,255,0.55)",
        marker_line_color="rgba(0,212,255,1)",
        marker_line_width=1.5
    )

    fig.update_layout(
        title="Phân phối ROA",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# INSIGHTS
# =====================================================

st.success("""
### 📌 Key Insights

• Asset Turnover là yếu tố tác động mạnh nhất đến ROA.

• Current Ratio và Pre-Tax Profit Margin có tác động tích cực.

• Net Profit Margin² cho thấy tác động phi tuyến đến ROA.

• Tương tác giữa Debt/Equity Ratio và Current Ratio làm giảm ROA.

• Mô hình giải thích được 62.54% biến động của ROA.

• Không phát hiện đa cộng tuyến nghiêm trọng (Max VIF < 10).
""")


    