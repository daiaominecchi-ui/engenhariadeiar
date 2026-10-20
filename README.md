# SENTINELA VISION — Inspeção 3D + Laboratório Sentinela 3.0

Protótipo **educacional** de diagnóstico industrial. Sem hardware necessário.

## Recursos

- Biblioteca de **4 máquinas**: motor elétrico, bomba centrífuga, esteira transportadora e compressor.
- Modelos **3D esquemáticos** interativos em Plotly; seleção de componentes e sintomas.
- Regras explicáveis de hipóteses e verificações; histórico temporário de casos; exportação PDF/JSON.
- Upload e prévia de fotos para organização da inspeção (**não há reconhecimento automático nem reconstrução 3D real**).
- Laboratório Sentinela 3.0 preservado na página `pages/02_Laboratorio_Sentinela_3.py`: simulação de motor, sensores, controle PI, falhas, sensor virtual, caixa-preta e relatórios.

## Instalação no Codespaces / Windows

Use Python 3.10+ e execute na pasta com `app.py`:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 0.0.0.0
```

No Codespaces, abra a porta 8501 em **Ports**. No Windows local, abra http://localhost:8501.

Testes: `python -m pytest -q`.

## Enviar para GitHub

Envie **o conteúdo desta pasta** para a raiz do repositório `engenhariadeiar`, evitando criar outra pasta `engenhariadeiar` dentro dela. Se você mantiver a versão antiga em subpasta, execute os comandos a partir da pasta que contém este `app.py`.

## Limites e segurança

Os modelos 3D são formas procedurais ilustrativas, não modelos CAD exatos. Não há IA multimodal, fotogrametria, diagnóstico certificado ou integração com máquina real. Nenhum sintoma garante uma causa única. A aplicação **não substitui** manuais, profissionais habilitados, bloqueio e etiquetagem, normas de segurança e inspeções presenciais. Não intervenha em sistemas energizados, pressurizados ou em movimento.
