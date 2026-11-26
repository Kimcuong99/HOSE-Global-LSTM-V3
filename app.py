from pathlib import Path
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "simulation" / "processed" / "hose_model_ready.csv"
MODEL_FILE = ROOT / "models" / "simulation" / "global_lstm_final.keras"
PRED_FILE = ROOT / "outputs" / "simulation" / "global_lstm_predictions.csv"
BENCH_FILE = ROOT / "outputs" / "simulation" / "benchmark_metrics.csv"

TEXT = {
"Tiếng Việt": {
"subtitle":"Nền tảng phân tích cổ phiếu và hỗ trợ quyết định đầu tư",
"overview":"Tổng quan thị trường","stocks":"Phân tích cổ phiếu","forecast":"Dự báo Global LSTM",
"evaluation":"Đánh giá mô hình","data":"Quản lý dữ liệu","language":"Ngôn ngữ",
"warning":"DỮ LIỆU MÔ PHỎNG — KHÔNG PHẢI DỮ LIỆU GIAO DỊCH THỰC TẾ HOSE",
"tickers":"Mã cổ phiếu","observations":"Số quan sát","industries":"Nhóm ngành","avgret":"Lợi suất bình quân",
"industry":"Ngành","ticker":"Mã cổ phiếu","price":"Giá điều chỉnh","volume":"Khối lượng",
"choose":"Chọn mã cổ phiếu","history":"Lịch sử giá điều chỉnh","volchart":"Khối lượng giao dịch",
"lastprice":"Giá điều chỉnh gần nhất","nextprice":"Giá dự báo minh họa","return":"Lợi suất dự báo",
"nottrained":"Chưa tìm thấy mô hình LSTM đã huấn luyện. Dự báo bên dưới là baseline trung bình lịch sử, không phải dự báo LSTM.",
"trained":"Đã tìm thấy mô hình LSTM. Dự báo chi tiết cần chạy pipeline và tạo dữ liệu đầu vào tương ứng.",
"metrics":"Chỉ số đánh giá","upload":"Tải dữ liệu CSV hoặc Excel","preview":"Xem trước dữ liệu tải lên",
"download":"Tải CSV mô phỏng","modelstatus":"Trạng thái mô hình","available":"Đã có file mô hình","missing":"Chưa huấn luyện",
"marketindex":"Chỉ số thị trường mô phỏng","sector":"Phân bổ theo ngành","disclaimer":"Các giá trị, khối lượng và kết quả mô hình được sinh từ dữ liệu tổng hợp nhân tạo. Không sử dụng làm khuyến nghị đầu tư."
},
"English": {
"subtitle":"Equity analytics and investment decision-support platform",
"overview":"Market Overview","stocks":"Stock Analysis","forecast":"Global LSTM Forecast",
"evaluation":"Model Evaluation","data":"Data Management","language":"Language",
"warning":"SIMULATED DATA — NOT ACTUAL HOSE MARKET DATA",
"tickers":"Tickers","observations":"Observations","industries":"Industries","avgret":"Average return",
"industry":"Industry","ticker":"Ticker","price":"Adjusted price","volume":"Volume",
"choose":"Select ticker","history":"Adjusted price history","volchart":"Trading volume",
"lastprice":"Latest adjusted close","nextprice":"Illustrative forecast price","return":"Forecast return",
"nottrained":"No trained LSTM model found. The value below is a historical-mean baseline, not an LSTM forecast.",
"trained":"A trained LSTM model file was found. Run the pipeline to generate aligned forecast inputs.",
"metrics":"Evaluation metrics","upload":"Upload CSV or Excel","preview":"Uploaded data preview",
"download":"Download simulation CSV","modelstatus":"Model status","available":"Model file found","missing":"Not trained",
"marketindex":"Synthetic market index","sector":"Industry distribution","disclaimer":"Prices, volumes and model outputs are generated synthetic values. Do not use as investment advice."
},
"简体中文": {
"subtitle":"股票分析与投资决策支持平台",
"overview":"市场概览","stocks":"股票分析","forecast":"Global LSTM预测",
"evaluation":"模型评估","data":"数据管理","language":"语言",
"warning":"模拟数据 — 并非HOSE真实市场数据",
"tickers":"股票数量","observations":"观测值","industries":"行业数量","avgret":"平均收益率",
"industry":"行业","ticker":"股票代码","price":"复权价格","volume":"成交量",
"choose":"选择股票代码","history":"复权价格走势","volchart":"成交量",
"lastprice":"最新复权收盘价","nextprice":"示意预测价格","return":"预测收益率",
"nottrained":"未找到已训练的LSTM模型。下方数值为历史均值基准，并非LSTM预测。",
"trained":"已找到LSTM模型文件。请运行完整流程以生成匹配的预测输入。",
"metrics":"评估指标","upload":"上传CSV或Excel","preview":"上传数据预览",
"download":"下载模拟CSV","modelstatus":"模型状态","available":"已找到模型文件","missing":"尚未训练",
"marketindex":"模拟市场指数","sector":"行业分布","disclaimer":"价格、成交量及模型结果均为人工合成数据，不构成投资建议。"
}}

st.set_page_config(page_title="HOSE Global LSTM | Equity Analytics", page_icon=None, layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:#f3f6fa;color:#17283e}
[data-testid="stSidebar"]{background:#102239}
[data-testid="stSidebar"] *{color:#f1f6fc}
.hero{padding:28px 32px;border-radius:18px;background:linear-gradient(115deg,#10243e,#174b68 65%,#087f8c);color:white;margin-bottom:18px}
.hero h1{font-family:Manrope,sans-serif;font-size:30px;font-weight:800;margin:0}
.hero p{margin:6px 0 0;color:#d8e8f3}
.notice{background:#fff2d9;border:1px solid #f0d39b;color:#754900;border-radius:10px;padding:11px 15px;font-weight:700;font-size:12px;letter-spacing:.25px}
.kpi{background:white;border:1px solid #e5ebf2;border-radius:14px;padding:17px 19px;box-shadow:0 3px 14px #1b36500a}
.kpi-label{font-size:12px;color:#718096;font-weight:600}
.kpi-value{font-size:26px;color:#152e49;font-weight:800;margin-top:5px}
.block-container{padding-top:1.8rem}
</style>
""", unsafe_allow_html=True)

if "ui_language" not in st.session_state:
    st.session_state.ui_language = "Tiếng Việt"

with st.sidebar:
    st.markdown("## ◈ HOSE / QUANT")
    st.caption("GLOBAL LSTM · RESEARCH TERMINAL")
    st.session_state.ui_language = st.selectbox(
        "Language / Ngôn ngữ / 语言",
        list(TEXT.keys()),
        index=list(TEXT.keys()).index(st.session_state.ui_language)
    )
    t = TEXT[st.session_state.ui_language]
    page = st.radio("WORKSPACE", [
        t["overview"], t["stocks"], t["forecast"], t["evaluation"], t["data"]
    ], label_visibility="collapsed")
    st.markdown("---")
    st.caption("V3.0.0  |  RESEARCH PLATFORM")

st.markdown(
    f'<div class="hero"><h1>HOSE GLOBAL LSTM</h1><p>{t["subtitle"]} · 2020—2025 · 160 configured tickers</p></div>',
    unsafe_allow_html=True
)
# Research data disclosure is retained in the page footer.

if not DATA_FILE.exists():
    st.error(f"Dataset not found: {DATA_FILE}. Run scripts/generate_hose_simulation.py first.")
    st.stop()

df = pd.read_csv(DATA_FILE, parse_dates=["date"])
df = df.drop(columns=["data_type", "data_source"], errors="ignore")
required = {"ticker","industry","date","close","adjusted_close","volume","next_day_return"}
missing = required - set(df.columns)
if missing:
    st.error(f"Dataset is missing required columns: {sorted(missing)}")
    st.stop()

def kpi(col, label, value):
    col.markdown(
        f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>',
        unsafe_allow_html=True
    )

if page == t["overview"]:
    st.subheader(t["overview"])
    cols = st.columns(4)
    kpi(cols[0], t["tickers"], f'{df.ticker.nunique():,}')
    kpi(cols[1], t["observations"], f'{len(df):,}')
    kpi(cols[2], t["industries"], f'{df.industry.nunique():,}')
    kpi(cols[3], t["avgret"], f'{df.next_day_return.mean()*100:.3f}%')
    left, right = st.columns([1.5,1])
    with left:
        market = df.groupby("date",as_index=False).next_day_return.mean()
        market["synthetic_index"] = 100*np.exp(market.next_day_return.fillna(0).cumsum())
        fig = px.line(market,x="date",y="synthetic_index",title=t["marketindex"],template="plotly_white")
        fig.update_layout(margin=dict(l=10,r=10,t=50,b=10),height=370)
        st.plotly_chart(fig,use_container_width=True)
    with right:
        sectors = df.groupby("industry",as_index=False).ticker.nunique()
        fig = px.bar(sectors,x="industry",y="ticker",title=t["sector"],template="plotly_white")
        fig.update_layout(margin=dict(l=10,r=10,t=50,b=10),height=370,xaxis_tickangle=-35)
        st.plotly_chart(fig,use_container_width=True)
elif page == t["stocks"]:
    st.subheader(t["stocks"])
    a,b = st.columns(2)
    industry = a.selectbox(t["industry"],["All"]+sorted(df.industry.unique().tolist()))
    subset = df if industry == "All" else df[df.industry == industry]
    ticker = b.selectbox(t["choose"],sorted(subset.ticker.unique().tolist()))
    s = subset[subset.ticker == ticker].sort_values("date")
    c1,c2,c3 = st.columns(3)
    c1.metric(t["lastprice"],f'{s.adjusted_close.iloc[-1]:,.0f}')
    c2.metric(t["volume"],f'{s.volume.iloc[-1]:,.0f}')
    c3.metric(t["avgret"],f'{s.next_day_return.mean()*100:.3f}%')
    fig = px.line(s,x="date",y="adjusted_close",title=f"{ticker} · {t['history']}",template="plotly_white")
    st.plotly_chart(fig,use_container_width=True)
    fig = px.bar(s.tail(180),x="date",y="volume",title=t["volchart"],template="plotly_white")
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(s.tail(30),use_container_width=True,hide_index=True)

elif page == t["forecast"]:
    st.subheader(t["forecast"])
    ticker = st.selectbox(t["choose"],sorted(df.ticker.unique().tolist()),key="forecast_ticker")
    s = df[df.ticker == ticker].sort_values("date")
    baseline = float(s.next_day_return.tail(60).mean())
    last_price = float(s.adjusted_close.iloc[-1])
    illustrative_price = last_price*np.exp(baseline)
    if MODEL_FILE.exists():
        st.info(t["trained"])
    else:
        st.info(t["nottrained"])
    c1,c2,c3 = st.columns(3)
    c1.metric(t["lastprice"],f"{last_price:,.0f}")
    c2.metric(t["nextprice"],f"{illustrative_price:,.0f}")
    c3.metric(t["return"],f"{baseline*100:.3f}%")
    fig = px.line(s.tail(180),x="date",y="adjusted_close",title=f"{ticker} · {t['history']}",template="plotly_white")
    st.plotly_chart(fig,use_container_width=True)

elif page == t["evaluation"]:
    st.subheader(t["evaluation"])
    st.caption("Test results are meaningful only after running the benchmark and LSTM training scripts.")
    if BENCH_FILE.exists():
        metrics = pd.read_csv(BENCH_FILE)
        st.dataframe(metrics,use_container_width=True,hide_index=True)
        if {"Model","MAE_Return","RMSE_Return"}.issubset(metrics.columns):
            long = metrics.melt(id_vars="Model",value_vars=["MAE_Return","RMSE_Return"],var_name="Metric",value_name="Value")
            st.plotly_chart(px.bar(long,x="Model",y="Value",color="Metric",barmode="group",template="plotly_white"),use_container_width=True)
    else:
        st.warning("No benchmark results yet. Run prepare_data.py then benchmark_models.py.")
    if PRED_FILE.exists():
        st.subheader("Global LSTM predictions")
        st.dataframe(pd.read_csv(PRED_FILE).head(100),use_container_width=True,hide_index=True)
    else:
        st.info("Global LSTM prediction file has not been generated.")

else:
    st.subheader(t["data"])
    st.write(f"**{t['modelstatus']}:** {t['available'] if MODEL_FILE.exists() else t['missing']}")
    upload = st.file_uploader(t["upload"],type=["csv","xlsx","xls"])
    if upload is not None:
        try:
            uploaded = pd.read_excel(upload) if upload.name.lower().endswith((".xlsx",".xls")) else pd.read_csv(upload)
            st.success(f"{len(uploaded):,} rows · {len(uploaded.columns)} columns")
            st.dataframe(uploaded.head(100),use_container_width=True,hide_index=True)
        except Exception as exc:
            st.error(f"Could not read uploaded file: {exc}")
    st.download_button(t["download"],df.to_csv(index=False).encode("utf-8-sig"),
                       file_name="hose_simulation.csv",mime="text/csv")



