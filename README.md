# DESAFIO-SCI-SISTEMAS — RAG com Strands Agents

Sistema de Retrieval-Augmented Generation (RAG) para atendimento ao cliente: responde perguntas com base num histórico real de conversas de suporte (pedidos, cancelamentos, promoções etc.), usando busca semântica em vez de regras fixas. Serve como backend de um chat de atendimento — CLI, API HTTP (`/chat`, `/chat/stream`) e frontend web já implementados.

## Deploy

- **App (frontend):** [desafio-sci.app.foliumdev.com.br](https://desafio-sci.app.foliumdev.com.br)
- **API (backend):** [desafio-sci.api.foliumdev.com.br](https://desafio-sci.api.foliumdev.com.br)
- **Observabilidade (Grafana):** [desafio-sci.telemetria.foliumdev.com.br](https://desafio-sci.telemetria.foliumdev.com.br)

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

## Como Rodar

### Pré-requisitos

- Python 3.10+, Docker (pra subir o Postgres local)
- Chave de API da OpenAI

### 1. Ambiente

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Banco de dados

```bash
docker compose up -d   # sobe Postgres com pgvector já habilitado (backend/docker-compose.yml)
```

### 3. Variáveis de ambiente

```bash
cp .env.example .env
```

Preencha `OPENAI_API_KEY` no `.env` — os demais valores (`DATABASE_URL`, `TOP_K`, etc.) já vêm com defaults que funcionam com o `docker compose` acima.

### 4. Popular a base de conhecimento

```bash
python -m ingestion.setup_db
python -m ingestion.embed_and_store
```

### 5. Subir a API

```bash
uvicorn api.main:app --app-dir src --reload
```

## Exemplo

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "meu pedido não chegou, o que faço?"}'
```

Resposta real (do relatório de testes, `backend/tests/relatorio_testes.md`):

> Se o seu pedido não chegou, o primeiro passo é verificar o status do seu pedido. Você pode fazer isso fornecendo o número do pedido ao atendente. É importante relatar a situação, especialmente se já se passou um tempo considerável desde a confirmação do pagamento. [...]

Também dá pra usar direto em Python: `from agent.agent import ask; ask("...")`.

## Decisões Técnicas

| Decisão | Escolha | Por quê (e não a alternativa) |
|---|---|---|
| Chunking | Conversa inteira, sem overlap | Overlap resolve corte de texto contínuo — problema que não existe em conversas curtas e autocontidas |
| Embeddings | `text-embedding-3-small` | Qualidade suficiente pro volume do dataset, custo menor que `-large` |
| Vector store | pgvector | Reaproveita o Postgres já usado, evitando uma peça de infra especializada (Pinecone, Weaviate) pra ~944 registros |
| Retrieval | top-k=3, threshold=0.40 | Threshold calibrado empiricamente (gap real entre scores dentro/fora do domínio) |
| LLM | `gpt-4o-mini` | Mesmo provedor dos embeddings, mais barato que `gpt-4o` e suficiente pro caso de uso |
| System Prompt | 7 regras, evoluída por teste | Regras 6 e 7 corrigem um bug real de alucinação de identidade encontrado em teste |

### Observabilidade

Traces e métricas do backend vão via OpenTelemetry para uma instância do **Grafana OTEL LGTM**: `openlit` instrumenta automaticamente as chamadas ao LLM (tokens, latência), `prometheus-fastapi-instrumentator` expõe métricas HTTP em `/metrics`, e spans manuais (`rag.pipeline`, `rag.retrieval`, `rag.embedding`, `rag.db_query`) cobrem o pipeline RAG, com logs em JSON correlacionados por `trace_id`. Optou-se pelo Grafana LGTM em vez de um dashboard próprio no front — ele já resolve isso pronto, poupando tempo do desafio pro sistema RAG em si. Configuração via `OTEL_EXPORTER_OTLP_ENDPOINT` e `OTEL_SERVICE_NAME`.

## Testes

```bash
python -m tests.test_evaluation
```

Gera `tests/relatorio_testes.md` com todas as perguntas e respostas. Última execução: 12/12 retrieval direto, 12/12 paráfrase, 8/8 fora do domínio — sem alucinação.

## Limitações e Melhorias Futuras

- **Dataset sintético:** conversas geradas por IA, não atendimentos reais.
- **Sem cache de embeddings:** perguntas repetidas geram nova chamada de embedding.
- **Sem busca híbrida:** busca puramente semântica, sem combinação com palavra-chave (prejudica buscas literais, tipo número de pedido).
- **Threshold fixo:** 0.40 calibrado com o dataset atual; precisa recalibrar com uso real em produção.
