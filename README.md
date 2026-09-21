# DESAFIO-SCI-SISTEMAS — RAG com Strands Agents

Sistema de Retrieval-Augmented Generation (RAG) que responde perguntas de atendimento ao cliente com base em conversas reais de suporte, usando busca semântica e o framework Strands Agents.

## Visão Geral

O sistema recebe uma pergunta em linguagem natural, busca as conversas de atendimento mais semanticamente relevantes numa base vetorial (pgvector) e usa esse contexto para gerar uma resposta via LLM — admitindo honestamente quando não sabe, em vez de inventar. O agente é construído com **Strands Agents** (framework model-driven da AWS): o próprio LLM decide quando consultar a base de conhecimento, via uma única tool de busca.

## Arquitetura

```
Pergunta do usuário
      │
      ▼
Agent (Strands + gpt-4o-mini)
      │  decide chamar a tool
      ▼
Tool: buscar_conhecimento
      │
      ▼
Embedding da pergunta (OpenAI text-embedding-3-small)
      │
      ▼
Busca por similaridade no pgvector (distância de cosseno, top-k=3)
      │
      ├── score < 0.40 → retorna "nada encontrado"
      │
      └── score ≥ 0.40 → retorna conversas relevantes formatadas
      │
      ▼
Agent sintetiza a resposta final com base no contexto recuperado
      │
      ▼
Resposta ao usuário
```

**Ingestão (offline, uma vez):** Dataset (.jsonl) → formatar conversa em texto → gerar embedding → gravar no pgvector.

## Decisões Técnicas

| Decisão | Escolha | Motivo resumido |
|---|---|---|
| Chunking | Conversa inteira, sem overlap | Conversas curtas e autocontidas |
| Embeddings | OpenAI `text-embedding-3-small` | Qualidade suficiente, custo menor que `large` |
| Vector store | pgvector | Reaproveita Postgres, sem infra especializada para ~944 registros |
| Retrieval | top-k=3, threshold=0.40 | Threshold calibrado empiricamente |
| LLM | OpenAI `gpt-4o-mini` | Mesmo provedor dos embeddings, rápido e suficiente |
| System Prompt | 7 regras, evoluída por teste | Regras 6 e 7 corrigem um bug real de alucinação de identidade |

### Observabilidade

Traces e métricas do backend vão via OpenTelemetry para uma instância do **Grafana OTEL LGTM**: `openlit` instrumenta automaticamente as chamadas ao LLM (tokens, latência), `prometheus-fastapi-instrumentator` expõe métricas HTTP em `/metrics`, e spans manuais (`rag.pipeline`, `rag.retrieval`, `rag.embedding`, `rag.db_query`) cobrem o pipeline RAG, com logs em JSON correlacionados por `trace_id`. Optou-se pelo Grafana LGTM em vez de um dashboard próprio no front, para poupar tempo do desafio. Configuração via `OTEL_EXPORTER_OTLP_ENDPOINT` e `OTEL_SERVICE_NAME`.

## Como Rodar

### Pré-requisitos
- Python 3.10+
- PostgreSQL com extensão `pgvector`
- Chave de API da OpenAI

### 1. Ambiente

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Variáveis de ambiente

```bash
cp .env.example .env
```
Preencha `OPENAI_API_KEY` e `DATABASE_URL` no `.env`.

### 3. Banco e ingestão

```bash
python -m ingestion.setup_db
python -m ingestion.embed_and_store
```

### 4. Perguntar ao agente

```bash
python -m agent.agent
```
Ou em código:
```python
from agent.agent import ask
print(ask("meu pedido não chegou, o que faço?"))
```

## Testes

```bash
python -m tests.test_evaluation
```
Gera `tests/relatorio_testes.md` com perguntas e respostas. Última execução: 12/12 retrieval direto, 12/12 paráfrase, 8/8 fora do domínio — sem alucinação.
