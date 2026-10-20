# SENTINELA — Caixa-preta de uma máquina

Simulador didático de motor/esteira, sensores, controlador PI, falhas e diagnóstico explicável. **Não precisa de hardware.**

## Executar no Windows ou Codespaces

Requer Python 3.10+.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

No Codespaces, abra a porta 8501 quando solicitado. No Windows, abra o endereço local indicado no terminal.

## Testes

```bash
python -m pytest -q
```

## Usar

1. Clique em **Simular** para criar uma linha de base.
2. Selecione uma falha no menu lateral e clique novamente em **Simular**.
3. Observe os gráficos e o diagnóstico, e exporte a telemetria e os eventos.
4. Use **Reiniciar** para começar outro ensaio.

## Limitações

Os parâmetros são ilustrativos; os dados não representam um equipamento calibrado. A simulação progride em lotes de 0,2 s, não em tempo real. A caixa-preta armazena até 5 segundos antes e depois de cada transição para uma falha; para eventos próximos, o registro anterior pode ser interrompido. O sensor virtual é uma aproximação estática, não um observador de estados validado. O diagnóstico de controle usa uma condição conhecida da simulação; não deve ser interpretado como identificação cega em equipamento real.
