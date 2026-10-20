from io import BytesIO
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape

def pdf_report(twin):
    out=BytesIO(); doc=SimpleDocTemplate(out); styles=getSampleStyleSheet()
    story=[Paragraph('SENTINELA 3.0 - Relatorio de simulacao',styles['Title']),Spacer(1,15),Paragraph('Modelo didatico. Resultados nao validados em equipamentos reais.',styles['Normal']),Spacer(1,12)]
    m=twin.metrics()
    for k,v in m.items(): story.append(Paragraph(f'{escape(str(k))}: {escape(str(v))}',styles['Normal']))
    story.append(Spacer(1,14)); story.append(Paragraph('Eventos diagnosticados',styles['Heading2']))
    if not twin.events: story.append(Paragraph('Nenhum evento detectado.',styles['Normal']))
    for e in twin.events:
        for txt in [f"Tempo: {e['time_s']:.1f}s | {e['diagnosis']}",f"Evidencia: {e['evidence']}",f"Acao: {e['action']}"]:
            story.append(Paragraph(escape(txt),styles['Normal']))
        story.append(Spacer(1,8))
    doc.build(story); return out.getvalue()
