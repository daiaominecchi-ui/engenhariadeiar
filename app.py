"""Sentinela Vision: interactive inspection demonstrator and gateway to legacy simulator."""
import io
import json
from datetime import datetime, timezone
import streamlit as st
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape
from sentinela.catalog import MACHINES, diagnose
from sentinela.visual import model

st.set_page_config(page_title='Sentinela Vision | Inspeção 3D',page_icon='🛠️',layout='wide')
st.markdown('''<style>.stApp{background:#0a1321;color:#e8f0fb}.block-container{padding-top:1rem;max-width:1500px}div[data-testid="stMetric"]{background:#142339;border:1px solid #29415c;border-radius:12px;padding:12px}h1,h2,h3{color:#f0f8ff}</style>''',unsafe_allow_html=True)
if 'cases' not in st.session_state: st.session_state.cases=[]
st.title('🛠️ SENTINELA VISION')
st.caption('Gêmeo digital esquemático • Inspeção orientada por sintomas • Laboratório Sentinela 3.0 integrado')
st.warning('Protótipo educacional. Os modelos 3D são esquemáticos e NÃO são reconstruções fotográficas nem CAD certificados. Hipóteses não substituem diagnóstico presencial, manual do fabricante ou procedimentos de segurança.')
mode=st.sidebar.radio('Módulos',['Inspeção 3D','Fotografias e cadastro','Casos e relatórios','Sobre o projeto'])
st.sidebar.info('Para simular telemetria, falhas, sensores virtuais e caixa-preta, abra **Laboratorio Sentinela 3** no menu de páginas do Streamlit.')

def pdf(cases):
    out=io.BytesIO(); doc=SimpleDocTemplate(out,pagesize=A4); styles=getSampleStyleSheet(); story=[Paragraph('SENTINELA VISION — Relatório de inspeção (simulação)',styles['Title']),Spacer(1,12)]
    story.append(Paragraph('Relatório educacional: as hipóteses não foram verificadas em equipamento real.',styles['Normal']))
    for i,c in enumerate(cases,1):
        story.append(Spacer(1,12));story.append(Paragraph(f"Caso {i}: {escape(c['machine'])} / {escape(c['component'])}",styles['Heading2']))
        story.append(Paragraph(f"Registro: {escape(c['created'])} | Sintomas: {escape(', '.join(c['symptoms']))}",styles['Normal']))
        story.append(Paragraph('Observações: '+escape(c['notes']),styles['Normal']))
        for d in c['diagnoses']:
            story.append(Paragraph('<b>'+escape(d['symptom'])+'</b>: '+escape(d['hypotheses']),styles['Normal']))
            story.append(Paragraph('Verificação: '+escape(d['verification']),styles['Normal']))
    doc.build(story);return out.getvalue()

if mode=='Inspeção 3D':
    left,right=st.columns([1,2])
    with left:
        machine=st.selectbox('Equipamento de demonstração',list(MACHINES))
        st.write(MACHINES[machine]['description'])
        component=st.selectbox('Componente sob investigação',MACHINES[machine]['components'])
        symptoms=st.multiselect('Sintomas observados',MACHINES[machine]['symptoms'])
        notes=st.text_area('Descrição do problema',placeholder='Ex.: ruído intermitente, após aumento de carga...')
        if st.button('🔍 Analisar sintomas',type='primary',use_container_width=True):
            if not symptoms: st.error('Selecione ao menos um sintoma.')
            else:
                findings=diagnose(machine,component,symptoms,notes)
                st.session_state.cases.append({'machine':machine,'component':component,'symptoms':symptoms,'notes':notes,'diagnoses':findings,'created':datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')})
                st.success('Análise registrada. Confira os resultados abaixo.')
    with right:
        st.plotly_chart(model(machine,component),use_container_width=True)
        st.caption('Gire com o mouse, aproxime com a roda e explore a geometria ilustrativa. Cor âmbar destaca componentes por correspondência aproximada de nome, não defeitos identificados.')
    st.subheader('Hipóteses técnicas')
    findings=diagnose(machine,component,symptoms,notes)
    if not findings: st.info('Escolha sintomas para visualizar hipóteses baseadas em regras.')
    for d in findings:
        with st.expander('⚠️ '+d['symptom'],expanded=True):
            st.write('**Causas possíveis:**',d['hypotheses']);st.write('**Verificação sugerida:**',d['verification']);st.caption(d['confidence'])
    st.info('Segurança: não execute intervenções com partes móveis, energizadas ou pressurizadas. Procedimentos de bloqueio, isolamento e qualificação profissional são indispensáveis.')
elif mode=='Fotografias e cadastro':
    st.subheader('📸 Fotografias da máquina')
    st.write('Envie fotos de vários ângulos para organizar a inspeção. **Esta versão não identifica automaticamente o modelo nem gera um 3D fiel a partir das imagens.** Para isso será necessário integrar um serviço de fotogrametria/visão computacional e validar o resultado.')
    uploads=st.file_uploader('Fotografias JPG/PNG',type=['jpg','jpeg','png'],accept_multiple_files=True)
    if uploads:
        st.success(f'{len(uploads)} arquivo(s) carregado(s) nesta sessão.')
        cols=st.columns(3)
        for i,up in enumerate(uploads):
            try:
                img=Image.open(up);img.verify();up.seek(0);img=Image.open(up)
                if img.width*img.height>24_000_000: st.warning(f'{up.name}: imagem muito grande para prévia.');continue
                with cols[i%3]: st.image(img,caption=f'{up.name} — {img.width}×{img.height}',use_container_width=True)
            except Exception: st.error(f'Arquivo inválido: {up.name}')
    st.markdown('**Para obter reconstrução geométrica de verdade:** fotos com boa sobreposição, escala de referência, captura de todos os lados visíveis e processamento especializado. Componentes internos não podem ser inferidos com confiabilidade só por fotografias externas.')
elif mode=='Casos e relatórios':
    st.subheader('📋 Histórico da sessão')
    st.caption('Os casos ficam apenas na sessão atual. Não existe persistência nem autenticação nesta versão.')
    if st.session_state.cases:
        for i,c in enumerate(st.session_state.cases,1):
            with st.expander(f"{i}. {c['machine']} — {c['component']} ({c['created']})"):
                st.write('Sintomas:',', '.join(c['symptoms']));st.write('Observações:',c['notes'] or 'Sem observações')
                for d in c['diagnoses']: st.write('•',d['symptom'],'—',d['hypotheses'])
        st.download_button('⬇ Baixar relatório PDF',pdf(st.session_state.cases),'sentinela_vision_inspecao.pdf','application/pdf')
        st.download_button('⬇ Baixar casos JSON',json.dumps(st.session_state.cases,ensure_ascii=False,indent=2).encode('utf-8'),'sentinela_vision_casos.json','application/json')
        if st.button('Limpar casos da sessão'):st.session_state.cases=[];st.rerun()
    else:st.info('Nenhum caso registrado. Vá até Inspeção 3D e analise um sintoma.')
else:
    st.markdown('''### Arquitetura integrada\n- **Sentinela Vision:** biblioteca de quatro equipamentos, visualização 3D esquemática, hipóteses por componente, fotos, casos e PDF.\n- **Sentinela 3.0:** motor e esteira simulados, controlador PI, oito cenários, sensor virtual, telemetria, diagnósticos, caixa-preta e exportação.\n\n### Limites técnicos\n- A geometria é ilustrativa, não reconstruída de fotografias.\n- As regras não têm precisão estatística medida nem dados industriais validados.\n- A plataforma não é um dispositivo de segurança, nem prevê falhas reais de modo certificado.\n- Não há contas de usuário, banco persistente ou serviço de IA externo.\n\n### Evoluções possíveis\nIntegração opcional com fotogrametria, biblioteca CAD/GLB de fabricantes, documentação técnica rastreável, autenticação, banco de dados e análise multimodal, sempre com validação humana.''')
