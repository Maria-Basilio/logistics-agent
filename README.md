# Logistics AI Agent

Agente de inteligência artificial para análise e apoio à tomada de decisão em operações logísticas.

O projeto combina regras determinísticas de logística com um agente de IA para responder perguntas sobre pedidos, veículos, entregas, estoque, prazos e consolidação de cargas.

## Funcionalidades

- Consulta de pedidos e prioridades
- Verificação de veículos disponíveis
- Recomendação de veículos com base em capacidade, origem e prioridade
- Identificação de veículos já alocados
- Consulta do status das entregas
- Identificação de pedidos sem veículo alocado
- Alertas de estoque abaixo do mínimo
- Análise de prazos de entrega
- Identificação de oportunidades de consolidação
- Resumos da operação logística
- Separação entre fatos operacionais e recomendações
- Testes automatizados

## Arquitetura

```text
logistics-agent/
│
├── data/
│   ├── deliveries.json
│   ├── inventory.json
│   ├── orders.json
│   └── vehicles.json
│
├── src/
│   ├── agent.py
│   ├── logistics.py
│   ├── main.py
│   └── tools.py
│
├── tests/
│   ├── test_agent.py
│   └── test_logistics.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md

## Tecnologias
- Python
- Ollama
- LLM (mopdelos de linguagem)
- pytest