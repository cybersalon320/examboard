import streamlit as st
from datetime import datetime
import pytz

# --- 1. 基礎配置 ---
st.set_page_config(page_title="專業考場看板", layout="wide")

# --- 2. 側邊欄設定 (連動手動輸入) ---
st.sidebar.header("📝 考場設定")
t_num = st.sidebar.number_input("應到人數", value=31, step=1)
p_num = st.sidebar.number_input("實到人數", value=30, step=1)
absent = t_num - p_num

st.sidebar.markdown("---")
default_sch = """第一節：自修, 08:25-09:10
第二節：寫作, 09:20-10:05
第三節：自修, 10:15-11:00
第四節：數學, 11:10-11:55
第五節：英文, 13:10-15:00
第六節：社會, 15:10-16:10"""

st.sidebar.subheader("📅 手動輸入考程")
raw_input = st.sidebar.text_area("格式：科目, 開始-結束", value=default_sch, height=250)
js_schedule = raw_input.strip().replace("\n", "\\n")

# --- 3. 渲染主畫面 (嵌入穩定 JS 邏輯) ---
# 這裡使用了 components.html，可以完美跑出你在 Colab 看到的流暢效果
import streamlit.components.v1 as components

html_content = f"""
<div id="main-container" style="background-color: #FDF5E6; padding: 40px; border-radius: 30px; font-family: sans-serif; color: #5D5D5D; min-width: 900px; margin: auto;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
        <div>
            <div id="time-label" style="font-size: 22px; font-weight: bold; color: #BC8F8F; margin-bottom: 5px;">當 前 時 間</div>
            <div id="clock" style="font-size: 100px; font-weight: bold; color: #5D5D5D; line-height: 1;">00:00:00</div>
        </div>
        <div id="subject-box" style="background: white; padding: 25px 50px; border-radius: 25px; text-align: right; box-shadow: 2px 2px 15px rgba(0,0,0,0.05);">
            <div id="cur-subject" style="font-size: 50px; font-weight: bold; color: #BC8F8F;">休息時間</div>
            <div id="cur-range" style="font-size: 26px; color: #888;">-- : --</div>
        </div>
    </div>

    <div style="display: flex; gap: 30px;">
        <div style="background: white; padding: 30px; border-radius: 25px; flex: 1; box-shadow: 2px 2px 10px rgba(0,0,0,0.02);">
            <div style="color: #BC8F8F; font-size: 24px; font-weight: bold; margin-bottom: 15px;">📅 今日考程表</div>
            <div id="schedule-list" style="border-top: 2px solid #FDF5E6; padding-top: 10px;"></div>
        </div>

        <div style="background: white; padding: 30px; border-radius: 25px; flex: 1.6; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.02);">
            <div style="color: #BC8F8F; letter-spacing: 12px; font-size: 22px; font-weight: bold; margin-bottom: 20px;">考 場 規 範</div>
            <div style="margin: 40px 0;">
                <span style="font-size: 60px; font-weight: bold; color: #333;">🚫 考完請在位靜候</span><br>
                <span style="font-size: 36px; color: #666;">等監考老師收完卷</span>
            </div>
            <div style="display: flex; justify-content: space-around; background: #FDF5E6; padding: 25px; border-radius: 20px; margin-top: 30px;">
                <div style="flex: 1;"><small>應到</small><br><b style="font-size: 55px;">{t_num}</b></div>
                <div style="flex: 1; border-left: 2px solid #ddd;"><small>實到</small><br><b style="font-size: 55px;">{p_num}</b></div>
                <div style="flex: 1; border-left: 2px solid #ddd;"><small>缺席</small><br><b style="font-size: 55px; color: {("#E63946" if absent > 0 else "#333")};">{absent}</b></div>
            </div>
        </div>
    </div>
</div>

<script>
const rawSchedule = "{js_schedule}";
const sch = rawSchedule.split('\\n').filter(line => line.includes(',')).map(line => {{
    const [n, t] = line.split(',');
    const [s, e] = t.trim().split('-');
    return {{ n: n.trim(), s: s.trim(), e: e.trim() }};
}});

function update() {{
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');
    const hm = h + ":" + m;
    document.getElementById('clock').innerText = h + ":" + m + ":" + s;

    let cur = "休息時間", rng = "-- : --", hiIdx = -1, isUrgent = false;
    sch.forEach((x, i) => {{
        if (hm >= x.s && hm <= x.e) {{
            cur = x.n; rng = x.s + " - " + x.e; hiIdx = i;
            const eParts = x.e.split(':');
            const eTime = new Date(); eTime.setHours(parseInt(eParts[0]), parseInt(eParts[1]), 0);
            const diff = (eTime - now) / 1000 / 60;
            if (diff >= 0 && diff <= 10) isUrgent = true;
        }}
    }});

    const warnRed = "#E63946";
    const themeBrown = "#BC8F8F";
    document.getElementById('clock').style.color = isUrgent ? warnRed : "#5D5D5D";
    document.getElementById('time-label').innerText = isUrgent ? "⚠️ 考試即將結束" : "當 前 時 間";
    document.getElementById('time-label').style.color = isUrgent ? warnRed : themeBrown;
    document.getElementById('subject-box').style.border = isUrgent ? "4px solid " + warnRed : "none";
    document.getElementById('cur-subject').innerText = cur;
    document.getElementById('cur-subject').style.color = isUrgent ? warnRed : themeBrown;
    document.getElementById('cur-range').innerText = rng;

    let listHtml = "";
    sch.forEach((x, i) => {{
        const isHi = i === hiIdx;
        listHtml += `<div style="background: ${{isHi ? '#A3B18A' : 'transparent'}}; color: ${{isHi ? 'white' : '#555'}}; border-radius: 12px; padding: 15px; display: flex; justify-content: space-between; font-size: 20px; margin-bottom: 8px;">
            <span>${{x.n}}</span><span>${{x.s}} - ${{x.e}}</span>
        </div>`;
    }});
    document.getElementById('schedule-list').innerHTML = listHtml;
}}
setInterval(update, 1000); update();
</script>
"""

components.html(html_content, height=850, scrolling=True)
