import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="D2C Pulse · Order Dashboard",
    page_icon="🍓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&family=Outfit:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

[data-testid="stAppViewContainer"] { background: #080b14 !important; color: #eef0f8; }
[data-testid="stSidebar"] { background: #0f1320 !important; border-right: 1px solid rgba(255,255,255,0.06); }
[data-testid="stSidebar"] * { color: #eef0f8 !important; }
[data-testid="stHeader"] { background: transparent !important; }

.block-container { padding-top: 2rem !important; }

h1, h2, h3 { font-family: 'Playfair Display', Georgia, serif !important; }

.metric-card {
    background: #0f1320;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 17px;
    padding: 20px 20px 17px;
    position: relative;
    overflow: hidden;
    margin-bottom: 8px;
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-2px); }
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 17px 17px 0 0;
}
.mc-1::before { background: #6c63ff; }
.mc-2::before { background: #ff6b8a; }
.mc-3::before { background: #2dd4bf; }
.mc-4::before { background: #fbbf24; }
.metric-icon { font-size: 22px; float: right; opacity: 0.15; margin-top: -4px; }
.metric-label { font-size: 10.5px; color: #6b738f; font-weight: 700; letter-spacing: 0.9px; text-transform: uppercase; margin-bottom: 10px; }
.metric-value { font-family: 'Playfair Display', Georgia, serif !important; font-size: 30px; font-weight: 900; color: #eef0f8; letter-spacing: -1.5px; line-height: 1; }
.metric-sub { font-size: 11.5px; color: #8892a8; margin-top: 6px; }
.metric-pill { display: inline-block; background: rgba(52,211,153,0.1); color: #34d399; border-radius: 6px; font-size: 10.5px; font-weight: 700; padding: 2px 8px; margin-top: 6px; }

.dash-title {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-size: 30px; font-weight: 900; letter-spacing: -1px;
    background: linear-gradient(135deg, #eef0f8 40%, #9f8fff 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.dash-sub { font-size: 13px; color: #6b738f; margin-top: 4px; }

.live-badge {
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(52,211,153,0.09); border: 1px solid rgba(52,211,153,0.28);
    color: #34d399; border-radius: 20px; font-size: 11.5px; font-weight: 600;
    padding: 5px 14px;
}

.upload-hero {
    text-align: center;
    padding: 80px 20px 60px;
}
.upload-hero-emoji { font-size: 56px; display: block; margin-bottom: 20px; }
.upload-hero-title {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-size: 38px; font-weight: 900; letter-spacing: -1.5px;
    background: linear-gradient(135deg, #eef0f8 30%, #9f8fff 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 12px;
}
.upload-hero-sub { font-size: 15px; color: #8892a8; line-height: 1.7; margin-bottom: 28px; }
.feat-row { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-top: 16px; }
.feat-pill { background: #0f1320; border: 1px solid rgba(255,255,255,0.06); border-radius: 20px; padding: 6px 14px; font-size: 12px; color: #8892a8; }

[data-testid="stFileUploader"] {
    background: rgba(108,99,255,0.04) !important;
    border: 2px dashed rgba(108,99,255,0.32) !important;
    border-radius: 14px !important;
    padding: 16px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #6c63ff !important;
    background: rgba(108,99,255,0.08) !important;
}

div[data-testid="metric-container"] {
    background: #0f1320;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 14px;
}

[data-testid="stTextInput"] > div > div {
    background: #0f1320 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 9px !important;
    color: #eef0f8 !important;
    font-family: 'Outfit', sans-serif !important;
}
[data-testid="stSelectbox"] > div > div {
    background: #0f1320 !important;
    color: #eef0f8 !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #6c63ff, #8b5cf6) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 9px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Data Loading ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data(file_bytes, filename):
    df = pd.read_excel(file_bytes)
    df.columns = df.columns.str.strip()
    df = df.drop(columns=[c for c in df.columns if str(c).strip() == ''], errors='ignore')
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    df['DOA'] = pd.to_datetime(df['DOA'], errors='coerce')
    df['Delivery Date'] = pd.to_datetime(df['Delivery Date'], errors='coerce')
    df['Month'] = df['Delivery Date'].dt.to_period('M').astype(str)
    df['Phone No.'] = df['Phone No.'].astype(str).str.strip()
    df['Name'] = df['Name'].astype(str).str.strip()
    df = df[df['Amount'] > 0]
    return df


PRODUCTS = [
    'Blueberries','Raspberries','Strawberry','Cherry',
    'FROZEN Blueberry','FROZEN Strawberries','Cup',
    'Darima Chilli Bomb','Darima Zarai','Darima Mild Cheddar',
    'Darima Farmhouse Cheddar','Darima Gouda Cheese','Darima Alpine Gruyere Cheese'
]
AC = ['#6c63ff','#ff6b8a','#2dd4bf','#fbbf24','#c084fc','#38bdf8','#fb923c']


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Playfair Display',serif;font-size:22px;font-weight:900;
         letter-spacing:-0.5px;margin-bottom:6px;display:flex;align-items:center;gap:8px;">
        <span style="background:linear-gradient(135deg,#6c63ff,#8b5cf6);border-radius:8px;
              width:28px;height:28px;display:inline-flex;align-items:center;justify-content:center;
              font-size:14px;">🍓</span>
        D2C Pulse
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**📂 Upload Data File**")
    uploaded = st.file_uploader(
        label="Drop your Excel file here",
        type=["xlsx", "xls"],
        label_visibility="collapsed"
    )

    if uploaded:
        st.success(f"✅ {uploaded.name}")
    st.markdown("---")
    st.markdown("**Navigation**")
    st.markdown("📊 Overview KPIs")
    st.markdown("📈 Charts & Trends")
    st.markdown("📋 All Records")
    st.markdown("---")
    st.caption("D2C Order Portfolio Dashboard")


# ── Upload Hero (shown when no file) ──────────────────────────────────────────
if not uploaded:
    st.markdown("""
    <div class="upload-hero">
        <span class="upload-hero-emoji">🍓</span>
        <div class="upload-hero-title">Order Portfolio Dashboard</div>
        <div class="upload-hero-sub">
            Upload your D2C Order Portfolio Excel file to instantly<br>
            visualise KPIs, product trends, and customer insights.
        </div>
        <div class="feat-row">
            <span class="feat-pill">🔒 Private & Secure</span>
            <span class="feat-pill">⚡ Instant Charts</span>
            <span class="feat-pill">📋 Full Records Table</span>
            <span class="feat-pill">⬇ CSV Export</span>
            <span class="feat-pill">🔄 Always Up-to-date</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Big centered uploader
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.file_uploader(
            "Upload your Excel file (.xlsx or .xls)",
            type=["xlsx","xls"],
            key="hero_upload",
            on_change=lambda: None
        )
    st.stop()


# ── Load Data ──────────────────────────────────────────────────────────────────
with st.spinner("🍓 Parsing your data…"):
    df = load_data(uploaded, uploaded.name)


# ── Dashboard Title ────────────────────────────────────────────────────────────
dates = df['Delivery Date'].dropna().sort_values()
dr = f"{dates.iloc[0].strftime('%b %Y')} – {dates.iloc[-1].strftime('%b %Y')}" if len(dates) else uploaded.name

col_title, col_badge = st.columns([4, 1])
with col_title:
    st.markdown(f'<div class="dash-title">Sales Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="dash-sub">D2C Order Portfolio · {dr} · {df.shape[0]:,} records</div>', unsafe_allow_html=True)
with col_badge:
    st.markdown('<br><div class="live-badge">🟢 Live File Data</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── KPI Cards ──────────────────────────────────────────────────────────────────
total_rev = df['Amount'].sum()
total_orders = len(df)
phone_counts = df['Phone No.'].value_counts()
unique_customers = len(phone_counts)
repeat_customers = (phone_counts > 1).sum()
repeat_rate = (repeat_customers / unique_customers * 100) if unique_customers else 0
avg_order = total_rev / total_orders if total_orders else 0

monthly = df.groupby('Month')['Amount'].sum()
peak_month = monthly.idxmax() if len(monthly) else ''
peak_val = monthly.max() if len(monthly) else 0

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f"""<div class="metric-card mc-1">
        <div class="metric-icon">💰</div>
        <div class="metric-label">Total Revenue</div>
        <div class="metric-value">₹{total_rev/100000:.2f}L</div>
        <div class="metric-pill">↑ Peak {peak_month}: ₹{peak_val/100000:.2f}L</div>
    </div>""", unsafe_allow_html=True)
with k2:
    st.markdown(f"""<div class="metric-card mc-2">
        <div class="metric-icon">📦</div>
        <div class="metric-label">Total Orders</div>
        <div class="metric-value">{total_orders:,}</div>
        <div class="metric-sub">Avg ₹{avg_order:,.0f} / order</div>
    </div>""", unsafe_allow_html=True)
with k3:
    st.markdown(f"""<div class="metric-card mc-3">
        <div class="metric-icon">👤</div>
        <div class="metric-label">Unique Customers</div>
        <div class="metric-value">{unique_customers:,}</div>
        <div class="metric-sub">{repeat_customers} repeat buyers</div>
    </div>""", unsafe_allow_html=True)
with k4:
    st.markdown(f"""<div class="metric-card mc-4">
        <div class="metric-icon">🔁</div>
        <div class="metric-label">Repeat Rate</div>
        <div class="metric-value">{repeat_rate:.1f}%</div>
        <div class="metric-pill">↑ Strong loyalty</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ── Chart helpers ─────────────────────────────────────────────────────────────
def chart_style(fig):
    fig.update_layout(
        paper_bgcolor='#0f1320', plot_bgcolor='#0f1320',
        font=dict(color='#6b738f', family='Outfit, sans-serif', size=12),
        title_font=dict(color='#eef0f8', size=15, family='Playfair Display, Georgia, serif'),
        margin=dict(l=8, r=8, t=40, b=8),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)', showgrid=True),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)', showgrid=True),
    )
    return fig


# ── Charts Row 1 ──────────────────────────────────────────────────────────────
st.markdown('<h3 style="font-family:\'Playfair Display\',serif;font-size:19px;font-weight:800;color:#eef0f8;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:10px;">📈 Trends & Performance</h3>', unsafe_allow_html=True)

c1, c2 = st.columns([2, 1])
with c1:
    mo = df.groupby('Month')['Amount'].sum().reset_index().sort_values('Month')
    fig = px.area(mo, x='Month', y='Amount', title='Monthly Revenue',
                  color_discrete_sequence=['#6c63ff'], template='plotly_dark')
    fig.update_traces(fill='tozeroy', fillcolor='rgba(108,99,255,0.14)',
                      line=dict(color='#6c63ff', width=2.5),
                      mode='lines+markers', marker=dict(size=7, color='#6c63ff'))
    fig.update_layout(xaxis_title='', yaxis_title='Revenue (₹)',
                      yaxis_tickformat=',.0f', hovermode='x unified')
    st.plotly_chart(chart_style(fig), use_container_width=True)

with c2:
    loc = df[df['Location'].notna() & (df['Location'] != 'Total')]
    loc_rev = loc.groupby('Location')['Amount'].sum().nlargest(6).reset_index()
    fig2 = px.bar(loc_rev, x='Amount', y='Location', orientation='h',
                  title='Revenue by Location',
                  color='Amount', color_continuous_scale=['#6c63ff','#ff6b8a'],
                  template='plotly_dark')
    fig2.update_layout(coloraxis_showscale=False, xaxis_title='', yaxis_title='',
                       xaxis_tickformat=',.0f')
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(chart_style(fig2), use_container_width=True)


# ── Charts Row 2 ──────────────────────────────────────────────────────────────
c3, c4, c5 = st.columns(3)
with c3:
    prod_cols = [p for p in PRODUCTS if p in df.columns]
    pq = {p.strip(): pd.to_numeric(df[p], errors='coerce').sum() for p in prod_cols}
    pq_df = pd.DataFrame(list(pq.items()), columns=['Product','Units']).sort_values('Units').tail(7)
    fig3 = px.bar(pq_df, x='Units', y='Product', orientation='h',
                  title='Top Selling Products',
                  color='Product', color_discrete_sequence=AC, template='plotly_dark')
    fig3.update_layout(showlegend=False, xaxis_title='', yaxis_title='')
    st.plotly_chart(chart_style(fig3), use_container_width=True)

with c4:
    new_c = unique_customers - repeat_customers
    fig4 = go.Figure(data=[go.Pie(
        labels=['Repeat', 'New'], values=[repeat_customers, new_c], hole=0.72,
        marker=dict(colors=['#6c63ff','rgba(255,255,255,0.055)'],
                    line=dict(color=['#6c63ff','rgba(255,255,255,0.07)'], width=2)),
    )])
    fig4.add_annotation(
        text=f"<b>{repeat_rate:.1f}%</b><br><span style='font-size:11px'>Repeat Rate</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=18, color='#eef0f8', family='Playfair Display,serif'), align='center'
    )
    fig4.update_layout(
        title='Repeat vs New Customers',
        paper_bgcolor='#0f1320', font=dict(color='#6b738f', family='Outfit,sans-serif'),
        title_font=dict(color='#eef0f8', size=15, family='Playfair Display,serif'),
        legend=dict(orientation='h', yanchor='bottom', y=-0.15, xanchor='center', x=0.5),
        margin=dict(l=8, r=8, t=40, b=8),
    )
    st.plotly_chart(fig4, use_container_width=True)

with c5:
    if 'Channel' in df.columns:
        ch = df['Channel'].value_counts().reset_index()
        ch.columns = ['Channel','Orders']
        fig5 = px.pie(ch.head(6), values='Orders', names='Channel',
                      title='Sales by Channel', hole=0.4,
                      color_discrete_sequence=AC, template='plotly_dark')
        fig5.update_layout(
            paper_bgcolor='#0f1320', font=dict(color='#6b738f', family='Outfit,sans-serif'),
            title_font=dict(color='#eef0f8', size=15, family='Playfair Display,serif'),
            legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5),
            margin=dict(l=8, r=8, t=40, b=8),
        )
        st.plotly_chart(fig5, use_container_width=True)


# ── Records Table ──────────────────────────────────────────────────────────────
st.markdown('<h3 style="font-family:\'Playfair Display\',serif;font-size:19px;font-weight:800;color:#eef0f8;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:10px;margin-top:28px;">📋 All Records</h3>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns([2, 2, 1.5, 1.5])
with f1:
    name_f = st.text_input("🔍 Filter by Name", placeholder="Search customer name…")
with f2:
    phone_f = st.text_input("📞 Filter by Phone", placeholder="Search phone number…")
with f3:
    status_opts = ['All'] + sorted(df['Delivery Status'].dropna().unique().tolist())
    status_f = st.selectbox("📦 Status", status_opts)
with f4:
    loc_opts = ['All'] + sorted(df['Location'].dropna().unique().tolist())
    loc_f = st.selectbox("📍 Location", loc_opts)

mask = pd.Series([True] * len(df), index=df.index)
if name_f:
    mask &= df['Name'].str.contains(name_f, case=False, na=False)
if phone_f:
    mask &= df['Phone No.'].str.contains(phone_f, na=False)
if status_f != 'All':
    mask &= df['Delivery Status'] == status_f
if loc_f != 'All':
    mask &= df['Location'] == loc_f

fdf = df[mask]

m1, m2, m3 = st.columns(3)
m1.metric("Filtered Records", f"{len(fdf):,}")
m2.metric("Filtered Revenue", f"₹{fdf['Amount'].sum()/100000:.2f}L")
m3.metric("Avg Order Value", f"₹{fdf['Amount'].mean():,.0f}" if len(fdf) else "₹0")

display_cols = ['S.no','Name','Phone No.','Location','Society Name','Unit of Punnet',
                'Strawberry','Blueberries','Raspberries','Cherry',
                'Amount','DOA','Delivery Date','Delivery Status','Payment Mode','Channel']
display_cols = [c for c in display_cols if c in fdf.columns]
tdf = fdf[display_cols].copy()
for dc in ['DOA','Delivery Date']:
    if dc in tdf.columns:
        tdf[dc] = tdf[dc].dt.strftime('%Y-%m-%d').fillna('-')

st.dataframe(
    tdf,
    use_container_width=True,
    height=480,
    hide_index=True,
    column_config={
        'Amount': st.column_config.NumberColumn('Amount (₹)', format="₹%,.0f"),
        'S.no':   st.column_config.NumberColumn('#', width='small'),
    }
)

d1, d2 = st.columns(2)
with d1:
    st.download_button(
        f"⬇ Download Filtered ({len(fdf):,} records)",
        data=fdf.to_csv(index=False).encode('utf-8'),
        file_name=f"D2C_filtered_{len(fdf)}_records.csv",
        mime='text/csv',
        use_container_width=True,
    )
with d2:
    st.download_button(
        "⬇ Download All Records",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="D2C_all_records.csv",
        mime='text/csv',
        use_container_width=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
