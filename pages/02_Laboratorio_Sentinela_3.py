import io
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sentinela.engine import Twin, SCENARIOS

st.set_page_config(page_title='SENTINELA 3.0 | Gêmeo Digital', page_icon='⚙️', layout='wide')
st.markdown('''<style>.stApp{background:#0b1220;color:#e6edf8}.block-container{padding-top:1.3rem}div[data-testid="stMetric"]{background:#152236;border:1px solid #28405a;border-radius:12px;padding:14px}h1,h2,h3{color:#e8f4ff}</style>''', unsafe_allow_html=True)
if 'twin' not in st.session_state: st.session_state.twin = Twin()
twin=st.session_state.twin
st.title('⚙️ SENTINELA 3.0 — Gêmeo Digital Industrial')
st.caption('Simulação didática de esteira e motor | Diagnóstico baseado em regras | NÃO utilizar para segurança ou manutenção de equipamentos reais')
with st.sidebar:
    st.header('Central de operação')
    scenario=st.selectbox('Condição simulada',SCENARIOS,index=SCENARIOS.index(twin.scenario))
    twin.set_scenario(scenario)
    twin.target=st.slider('Referência de velocidade (rpm)',300,1500,int(twin.target),50)
    twin.enabled=st.toggle('Motor habilitado',value=twin.enabled)
    steps=st.slider('Avançar simulação (segundos)',2,60,10,2)
    if st.button('▶ Avançar simulação',use_container_width=True,type='primary'):
        twin.run(int(steps/twin.dt))
    if st.button('⟳ Reiniciar experimento',use_container_width=True):
        st.session_state.twin=Twin(); st.rerun()
    st.info('O tempo avança quando você clica no botão. Assim, a simulação é reproduzível e não exige processos em segundo plano.')
if not twin.history: twin.run(40)
h=pd.DataFrame(twin.history)
r=h.iloc[-1]
a,b,c,d=st.columns(4)
a.metric('Velocidade real',f"{r['speed_rpm']:.0f} rpm")
b.metric('Corrente',f"{r['current_a']:.1f} A")
c.metric('Temperatura',f"{r['temp_c']:.1f} °C")
d.metric('Vibração',f"{r['vibration_mms']:.2f} mm/s")
current=twin.diagnose()
if current:
    st.error('🚨 '+current['title']+' — confiança qualitativa: '+current['confidence'])
    st.write('**Evidência:** '+current['evidence']+'  **Ação sugerida:** '+current['action'])
else: st.success('Sem anomalia diagnosticada pelas regras atuais. Isso não garante ausência de falhas.')
tab1,tab2,tab3,tab4=st.tabs(['📊 Telemetria','🏭 Gêmeo digital 3D','🧠 Investigação','📁 Relatórios'])
with tab1:
    for names,title in [(['speed_rpm','sensor_rpm','virtual_rpm','target_rpm'],'Velocidades (rpm)'),(['current_a','vibration_mms'],'Corrente (A) e vibração (mm/s): escalas distintas'),(['temp_c','wear_pct'],'Temperatura (°C) e desgaste (%)')]:
        fig=go.Figure()
        for name in names: fig.add_trace(go.Scatter(x=h.t,y=h[name],name=name,mode='lines'))
        fig.update_layout(title=title,template='plotly_dark',height=290,margin=dict(l=20,r=20,t=45,b=20),legend=dict(orientation='h'))
        st.plotly_chart(fig,use_container_width=True)
with tab2:
    st.write('Representação 3D esquemática da esteira; o movimento é indicado pela velocidade calculada, não por animação física.')
    fig=go.Figure()
    for y in (-1,1):
        fig.add_trace(go.Scatter3d(x=[0,8],y=[y,y],z=[0,0],mode='lines',line=dict(width=13,color='#66b4cf'),showlegend=False))
    for x in (0.6,2,3.4,4.8,6.2,7.4):
        fig.add_trace(go.Scatter3d(x=[x,x],y=[-1,1],z=[0,0],mode='lines',line=dict(width=5,color='#314d6c'),showlegend=False))
    fig.add_trace(go.Scatter3d(x=[4],y=[0],z=[0.2],mode='markers+text',marker=dict(size=18,color='#ffba57' if current else '#42dfac'),text=['Motor / Esteira'],textposition='top center',name='Equipamento'))
    fig.update_layout(template='plotly_dark',height=410,scene=dict(xaxis_title='Comprimento (m)',yaxis_title='Largura (m)',zaxis_title='Altura (m)',aspectmode='manual',aspectratio=dict(x=2.8,y=1,z=.7)),margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig,use_container_width=True)
    st.metric('Velocidade da esteira (aproximação)',f"{r['speed_rpm']*0.1*3.14159265/60:.2f} m/s")
    st.caption('Conversão ilustrativa com rolete de raio 0,05 m e transmissão 1:1; parâmetros hipotéticos.')
with tab3:
    st.subheader('Linha do tempo de diagnósticos')
    if twin.events:
        ev=pd.DataFrame([{k:v for k,v in e.items() if k not in ('pre_samples','post_samples')} for e in twin.events])
        st.dataframe(ev,use_container_width=True,hide_index=True)
        idx=st.selectbox('Investigar evento',range(len(twin.events)),format_func=lambda i:f"{twin.events[i]['time_s']:.1f}s — {twin.events[i]['diagnosis']}")
        event=twin.events[idx]
        st.write('**Evidência:**',event['evidence'])
        st.write('**Verificação sugerida:**',event['action'])
        st.caption(f"Janela da caixa-preta: {len(event['pre_samples'])} amostras anteriores e {len(event['post_samples'])} posteriores (até 10 s por lado).")
        samples=pd.DataFrame(event['pre_samples']+event['post_samples'])
        if not samples.empty: st.line_chart(samples.set_index('t')[['speed_rpm','sensor_rpm','virtual_rpm']])
    else: st.info('Nenhum evento detectado. Selecione uma falha e avance a simulação.')
    st.subheader('Indicadores de avaliação')
    st.json(twin.metrics())
    st.caption('Métricas simplificadas: detecção por cenário, sem matriz de confusão ou validação em dados reais.')
with tab4:
    st.download_button('⬇ Exportar telemetria CSV',h.to_csv(index=False).encode('utf-8-sig'),'sentinela_telemetria.csv','text/csv')
    payload={'metadata':{'version':'3.0','simulation_only':True,'dt_s':twin.dt},'metrics':twin.metrics(),'events':twin.events}
    st.download_button('⬇ Exportar caixa-preta JSON',json.dumps(payload,ensure_ascii=False,indent=2).encode('utf-8'),'sentinela_caixa_preta.json','application/json')
    if st.button('Gerar relatório PDF'):
        from sentinela.reporting import pdf_report
        st.download_button('⬇ Baixar relatório PDF',pdf_report(twin),'sentinela_relatorio.pdf','application/pdf')
    st.caption('Os arquivos são gerados localmente na sessão. Nenhum dado real é coletado.')
