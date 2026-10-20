"""Curated demonstration machines and component-based rule explanations."""
MACHINES = {
 'Motor elétrico': {'kind':'motor','description':'Motor de indução esquemático','components':['Rolamentos','Eixo','Ventilador','Enrolamentos','Acoplamento'], 'symptoms':['Vibração excessiva','Superaquecimento','Ruído anormal','Perda de velocidade','Consumo elevado']},
 'Bomba centrífuga': {'kind':'pump','description':'Bomba com corpo hidráulico e motor','components':['Rotor','Selo mecânico','Rolamentos','Tubulação de sucção','Motor'], 'symptoms':['Vibração excessiva','Vazamento','Ruído anormal','Baixa vazão','Superaquecimento']},
 'Esteira transportadora': {'kind':'conveyor','description':'Esteira industrial com roletes e acionamento','components':['Correia','Roletes','Motor','Redutor','Estrutura'], 'symptoms':['Desalinhamento','Vibração excessiva','Ruído anormal','Perda de velocidade','Superaquecimento']},
 'Compressor de ar': {'kind':'compressor','description':'Compressor com reservatório esquemático','components':['Cabeçote','Válvulas','Filtro de ar','Motor','Reservatório'], 'symptoms':['Baixa pressão','Superaquecimento','Vibração excessiva','Ruído anormal','Vazamento']},
}
RULES = {
 'Vibração excessiva': ('Desbalanceamento, desalinhamento, folgas ou desgaste de rolamentos.', 'Comparar tendência de vibração; inspecionar fixações e alinhamento após isolamento de energia.'),
 'Superaquecimento': ('Sobrecarga, ventilação insuficiente, atrito ou lubrificação inadequada.', 'Revisar histórico de carga e temperatura; inspecionar ventilação e lubrificação conforme manual.'),
 'Ruído anormal': ('Folga, contato indevido, cavitação (em bombas) ou desgaste mecânico.', 'Registrar frequência e localização do ruído; investigar somente com procedimento seguro.'),
 'Perda de velocidade': ('Carga excessiva, escorregamento, controle inadequado ou falha no sensor.', 'Comparar comando, corrente e medição independente de rotação.'),
 'Consumo elevado': ('Carga mecânica elevada, atrito ou anomalia elétrica.', 'Comparar corrente com carga e especificações de placa por profissional habilitado.'),
 'Vazamento': ('Vedação degradada, conexão frouxa ou pressão fora da faixa.', 'Isolar, despressurizar e inspecionar vedação conforme manual.'),
 'Baixa vazão': ('Obstrução, ar na sucção, desgaste do rotor ou cavitação.', 'Verificar condições de sucção e filtros; evitar operação a seco.'),
 'Desalinhamento': ('Tensionamento desigual, roletes desalinhados ou desgaste da correia.', 'Inspecionar guias e tensionamento com a esteira bloqueada.'),
 'Baixa pressão': ('Vazamentos, filtro obstruído, válvula defeituosa ou desgaste interno.', 'Verificar manômetros e histórico; despressurizar antes de intervenções.'),
}
def diagnose(machine, component, symptoms, notes=''):
    if machine not in MACHINES or component not in MACHINES[machine]['components']:
        raise ValueError('Máquina ou componente inválido')
    if not symptoms: return []
    result=[]
    for symptom in symptoms:
        if symptom not in MACHINES[machine]['symptoms']: continue
        cause, check = RULES[symptom]
        if machine=='Bomba centrífuga' and symptom=='Ruído anormal':
            cause='Cavitação, ar na sucção, folga ou desgaste de rolamentos.'
        result.append({'machine':machine,'component':component,'symptom':symptom,'hypotheses':cause,'verification':check,'confidence':'Não quantificada — requer dados reais'})
    return result
