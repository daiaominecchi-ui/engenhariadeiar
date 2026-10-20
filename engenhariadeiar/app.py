import json
import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sentinela.core import Simulator

st.set_page_config(page_title="Sentinela | Caixa-preta industrial", page_icon="🛠️", layout="wide")
st.title("🛠️ SENTINELA — Caixa-preta de uma máquina")
st.caption("Gêmeo digital educacional de motor e esteira • sensores virtuais • diagnóstico explicável")
if "sim" not in st.session_state:
    st.session_state.sim = Simulator()

with st.sidebar:
    st.header("Operação")
    setpoint = st.slider("Velocidade desejada (%)", 0, 150, 100)
    fault = st.selectbox("Injetar falha", ["Nenhuma", "Sobrecarga mecânica", "Sensor travado", "Ruído no sensor", "Perda de comunicação", "Controle mal ajustado"])
    steps = st.slider("Passos por execução", 1, 200, 40)
    run = st.button("▶ Simular", type="primary", use_container_width=True)
    if st.button("↺ Reiniciar", use_container_width=True):
        st.session_state.sim = Simulator()
        st.rerun()

sim = st.session_state.sim
if run:
    for _ in range(steps):
        sim.step(setpoint, fault)

if not sim.history:
    st.info("Clique em **Simular** para gerar os primeiros dados. Cada passo representa 0,2 segundo de tempo simulado.")
else:
    df = pd.DataFrame([vars(s) for s in sim.history])
    last = sim.history[-1]
    a,b,c,d = st.columns(4)
    a.metric("Velocidade medida", "Sem sinal" if math.isnan(last.speed) else f"{last.speed:.1f}%")
    b.metric("Corrente", f"{last.current:.2f} A")
    c.metric("Temperatura", f"{last.temperature:.1f} °C")
    d.metric("Vibração", f"{last.vibration:.2f} u.a.")
    st.subheader("Investigação")
    st.write(last.diagnosis)
    fig = go.Figure()
    for col, name in [("speed","Velocidade medida"),("estimated_speed","Sensor virtual"),("setpoint","Referência")]:
        fig.add_trace(go.Scatter(x=df.t,y=df[col],mode="lines",name=name))
    fig.update_layout(title="Velocidade e estimativa", xaxis_title="Tempo simulado (s)", yaxis_title="Velocidade (%)", height=360)
    st.plotly_chart(fig, use_container_width=True)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df.t,y=df.current,name="Corrente (A)"))
    fig2.add_trace(go.Scatter(x=df.t,y=df.vibration,name="Vibração (u.a.)",yaxis="y2"))
    fig2.update_layout(title="Corrente e vibração",xaxis_title="Tempo (s)",yaxis=dict(title="Corrente (A)"),yaxis2=dict(title="Vibração",overlaying="y",side="right"),height=320)
    st.plotly_chart(fig2, use_container_width=True)
    st.subheader("Caixa-preta: eventos")
    st.caption("Cada evento captura até 25 amostras anteriores e 25 posteriores à injeção (5 s de cada lado).")
    if sim.events:
        st.dataframe(pd.DataFrame([{"tempo":e['time'],"falha":e['fault'],"pré":len(e['pre']),"pós":len(e['post'])} for e in sim.events]),use_container_width=True)
        st.download_button("Baixar eventos JSON", json.dumps(sim.events, ensure_ascii=False, indent=2, default=str).encode("utf-8"),"eventos_sentinela.json","application/json")
    else:
        st.write("Nenhum evento registrado. Escolha uma falha e clique em Simular.")
    st.download_button("Baixar telemetria CSV",df.to_csv(index=False).encode("utf-8-sig"),"telemetria_sentinela.csv","text/csv")

st.divider()
st.caption("Protótipo de ensino: modelos e limiares são ilustrativos, não validados para segurança ou manutenção de equipamentos reais.")
