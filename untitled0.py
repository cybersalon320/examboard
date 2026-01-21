import streamlit as st
from datetime import datetime
import pytz
import streamlit.components.v1 as components

# --- 1. 配置 ---
st.set_page_config(page_title="專業考場看板", layout="wide")

# --- 2. 處理網址參數 (讀取同步數據) ---
params = st.query_params

st.sidebar.header("📝 考場設定")

# 讀取網址裡的人數，如果網址沒有，就用預設值 31/30
t_num = st.sidebar.number_input("應到人數", value=int(params.get("t", 31)), step=1)
p_num = st.sidebar.number_input("實到人數", value=int(params.get("p", 30)), step=1)
absent = t_num - p_num

st.sidebar.markdown("---")
default_sch_text = """第一節：自修, 08:25-09:10
第二節：寫作, 09:20-10:05
第三節：自修, 10:15-11:00
第四節：數學, 11:10-11:55
第五節：英文, 13:10-15:00
第六節：社會, 15:10-16:10"""

raw_input = st.sidebar.text_area("📅 手動輸入考程", value=default_sch_text, height=250)
js_schedule = raw_input.strip().replace("\n", "\\n")

# --- 核心同步按鈕 ---
if st.sidebar.button("🚀 點我同步數據到網址"):
    # 強制將現在的人數寫入網址
    st.query_params.update(t=t_num, p=p_num)
    st.sidebar.success("同步成功！現在可以複製上方網址分享了。")

# --- 3. 顯示看板 (JavaScript 部分) ---
html_content = f"""
<div id="main-container" style="background-color: #FDF5E6; padding: 40px; border-radius: 30px; font-family: sans-serif; color: #5D5D5D;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
        <div>
            <div id="time-label" style="font-size: 22px; font-weight: bold; color: #BC8F8F;">當 前 時 間</div>
            <div id="clock" style="font-size: 100px; font-weight: bold; color: #5D5D5D; line-height: 1;">00:00:00</div>
        </div>
        <div id="subject-box" style="background: white; padding: 25px 50px; border-radius: 25px; text-align: right; box-shadow: 2px 2px 15px rgba(0,0,0,0.05);">
            <div id="cur-subject" style="font-size: 50px; font-weight: bold; color: #BC8F8F;">載入中...</div>
            <div id="cur-range" style="font-size: 26px; color: #888;">-- : --</div>
        </div>
    </div>
    <div style="display: flex; gap: 30px;">
        <div style="background: white; padding: 30px; border-radius: 25px; flex: 1;">
            <div style="color: #BC8F8F; font-size: 24px; font-weight: bold; margin-bottom: 15px;">📅 今日考程表</div>
            <div id="schedule-list"></div>
        </div>
        <div style="background: white; padding: 30px; border-radius: 25px; flex: 1.6; text-align: center;">
            <b style="color: #BC8F8F; letter-spacing: 12px; font-size: 22px;">考 場 規 範</b>
            <h1 style="font-size: 60px; font-weight: bold; color: #333; margin: 40px 0;">🚫 考完請在位靜候<br><span style="font-size: 36px; color: #666;">等監考老師收完卷</span></h1>
            <div style="display: flex; justify-content: space-around; background: #FDF5E6; padding: 25px; border-radius: 20px;">
                <div><small>應到</small><br><b style="font-size: 55px;">{t_num}</b></div>
                <div><small>實到</small><br><b style="font-size: 55px;">{p_num}</b></div>
                <div><small>缺席</small><br><b style="font-size: 55px; color: {('#E63946' if absent > 0 else '#333')};">{absent}</b></div>
            </div>
        </div>
    </div>
</div>
<script>
const rawSch = "{js_schedule}";
const sch = rawSch.split('\\n').filter(l => l.includes(',')).map(l => {{
    const [n, t] = l.split(','); const [s, e] = t.trim().split('-');
    return {{ n: n.trim(), s: s.trim(), e: e.trim() }};
}});
function update() {{
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0'), m = String(now.getMinutes()).padStart(2, '0'), s = String(now.getSeconds()).padStart(2, '0');
    const hm = h + ":" + m;
    document.getElementById('clock').innerText = h + ":" + m + ":" + s;
    let cur = "休息時間", rng = "-- : --", hi = -1, urgent = false;
    sch.forEach((x, i) => {{
        if (hm >= x.s && hm <= x.e) {{
            cur = x.n; rng = x.s + " - " + x.e; hi = i;
            const ep = x.e.split(':'), et = new Date(); et.setHours(ep[0], ep[1], 0);
            if ((et - now)/60000 <= 10 && (et - now) > 0) urgent = true;
        }}
    }});
    document.getElementById('clock').style.color = urgent ? "#E63946" : "#5D5D5D";
    document.getElementById('cur-subject').innerText = cur;
    document.getElementById('cur-subject').style.color = urgent ? "#E63946" : "#BC8F8F";
    document.getElementById('cur-range').innerText = rng;
    let lh = "";
    sch.forEach((x, i) => {{
        const isH = i === hi;
        lh += `<div style="background: ${{isH ? '#A3B18A' : 'transparent'}}; color: ${{isH ? 'white' : '#555'}}; border-radius: 12px; padding: 15px; display: flex; justify-content: space-between; font-size: 20px; margin-bottom: 8px;">
            <span>${{x.n}}</span><span>${{x.s}} - ${{x.e}}</span>
        </div>`;
    }});
    document.getElementById('schedule-list').innerHTML = lh;
}}
setInterval(update, 1000); update();
</script>
"""

components.html(html_content, height=850)
