# DESAFIO-SCI-SISTEMAS — RAG com Strands Agents

Sistema de Retrieval-Augmented Generation (RAG) que responde perguntas de atendimento ao cliente com base em uma coleção de conversas reais de suporte, usando busca semântica e o framework Strands Agents.

## Visão Geral

O sistema recebe uma pergunta em linguagem natural, busca as conversas de atendimento mais semanticamente relevantes numa base vetorial (pgvector), e usa esse contexto para gerar uma resposta natural via LLM. Quando não há informação relevante na base, o sistema admite honestamente que não sabe, em vez de inventar uma resposta.

O agente é construído com o **Strands Agents** (framework model-driven da AWS): em vez de um fluxo de código rígido, o próprio LLM decide quando consultar a base de conhecimento, com base numa única tool de busca disponibilizada a ele.

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

**Fluxo de ingestão (offline, executado uma vez):**
```
Dataset (.jsonl) → formatar conversa em texto → gerar embedding → gravar no pgvector
```

## Decisões Técnicas

Resumo das principais decisões — a justificativa completa de cada uma, incluindo alternativas consideradas e evidências de calibração, está em [`DECISOES.md`](./DECISOES.md).

| Decisão | Escolha | Motivo resumido |
|---|---|---|
| Chunking | Conversa inteira, sem overlap | Conversas curtas e autocontidas; overlap resolve um problema (corte de texto contínuo) que não existe aqui |
| Embeddings | OpenAI `text-embedding-3-small` | Qualidade suficiente para o volume e complexidade do dataset, custo menor que o modelo `large` |
| Vector store | pgvector | Reaproveita infraestrutura já dominada (Postgres), sem necessidade de peça de infra especializada para ~944 registros |
| Retrieval | top-k=3, threshold=0.40 | Threshold calibrado empiricamente com evidência real (gap entre scores dentro/fora do domínio) |
| LLM | OpenAI `gpt-4o-mini` | Mesmo provedor dos embeddings (stack simples), rápido e suficiente para o caso de uso |
| System Prompt | 7 regras, evoluída por teste | Regras 6 e 7 nasceram de um bug real encontrado em teste (alucinação de identidade de negócio) |

## Como Rodar

### Pré-requisitos
- Python 3.10+
- PostgreSQL com extensão `pgvector` disponível
- Chave de API da OpenAI

### 1. Clonar e configurar o ambiente
```bash
git clone <url-do-repositorio>
cd DESAFIO-SCI-SISTEMAS/backend

python -m venv .venv
# Linux/Mac:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente
Copie `.env.example` para `.env` e preencha com suas credenciais reais:
```bash
cp .env.example .env
```
Variáveis necessárias:
```
OPENAI_API_KEY=sua_chave_aqui
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_do_banco
```

### 3. Criar a tabela no banco
```bash
python -m ingestion.setup_db
```

### 4. Rodar a ingestão (popula a base de conhecimento)
```bash
python -m ingestion.embed_and_store
```
Isso processa o dataset completo (~944 conversas) e grava embeddings no pgvector. Leva alguns minutos, com log de progresso a cada 50 conversas processadas.

### 5. Fazer perguntas ao agente
```bash
python -m agent.agent
```
Ou, em código:
```python
from agent.agent import ask

resposta = ask("meu pedido não chegou, o que faço?")
print(resposta)
```

## Estrutura de Pastas

```
backend/
├── .venv/                      # ambiente virtual (não versionado)
├── data/
│   └── dataset.jsonl           # dataset de conversas de atendimento
├── src/
│   ├── ingestion/
│   │   ├── loader.py           # carrega e formata as conversas (texto p/ embedding)
│   │   ├── setup_db.py         # cria a extensão pgvector e a tabela
│   │   └── embed_and_store.py  # gera embeddings e popula o banco
│   ├── retrieval/
│   │   └── search.py           # busca por similaridade no pgvector
│   ├── agent/
│   │   ├── tools.py            # tool @tool que encapsula a busca
│   │   ├── prompts.py          # system prompt do agente
│   │   └── agent.py            # monta o Agent (Strands) e expõe ask()
│   └── main.py                 # ponto de entrada
├── tests/
│   └── test_evaluation.py      # bateria de testes formais (retrieval, paráfrase, fora do domínio)
├── .env / .env.example
├── .gitignore
├── requirements.txt
├── DECISOES.md                 # justificativa detalhada de cada decisão técnica
└── README.md
```

## Testes

A bateria de testes cobre os requisitos obrigatórios do desafio, rodando via:
```bash
python -m tests.test_evaluation
```
Isso gera um relatório em `tests/relatorio_testes.md` com todas as perguntas e respostas obtidas.

**Resultado da última execução:**
- **Retrieval direto:** 12/12 perguntas retornaram respostas coerentes com o tema esperado, cobrindo 6 intents (saudação, dúvida de serviço, dúvida de produto, cancelamento, compra, elogio) e múltiplos setores do dataset.
- **Paráfrase:** 12/12 pares (pergunta original + reformulação com vocabulário totalmente diferente) mantiveram respostas consistentes entre si — confirma que a busca é semântica, não apenas por palavra-chave.
- **Fora do domínio:** 8/8 perguntas sem correspondência real na base foram recusadas corretamente, sem alucinação (uma pergunta inicialmente presumida como "fora do domínio" revelou, durante a investigação, ter correspondência real no setor de saúde da base — o sistema respondeu corretamente com base em conteúdo real; ver `DECISOES.md`, seção de observações).

Durante os testes, um bug real foi encontrado e corrigido: o agente generalizava incorretamente uma única conversa de exemplo como representativa de "toda a empresa" (ex: perguntado sobre carros, afirmou atuar no setor imobiliário com base numa única conversa parecida). Corrigido via ajuste na system prompt — detalhes completos em `DECISOES.md`, item 7.

## Limitações e Melhorias Futuras

- **Dataset sintético:** as conversas foram geradas por IA (não são atendimentos reais), o que pode significar menor variabilidade de linguagem real do que dados de produção.
- **Sem cache de embeddings:** perguntas repetidas geram uma nova chamada de embedding a cada vez; um cache simples reduziria custo e latência em uso repetido.
- **Sem busca híbrida:** a busca é puramente semântica (vetorial); buscas muito literais (números de pedido, nomes exatos de produto) poderiam se beneficiar de busca por palavra-chave combinada.
- **Threshold fixo:** o valor de 0.40 foi calibrado com o dataset atual; em produção, valeria monitorar e recalibrar com perguntas reais de usuários.
- **Sem interface de chat:** a interação atual é via função Python (`ask()`); uma interface web com streaming está entre os extras não implementados neste prazo.
- **Sem exibição de fontes:** os metadados (`conversation_id`, `similarity`) já são retornados pela tool internamente, mas não são expostos na resposta final ao usuário — implementação futura simples, dado que os dados já estão disponíveis no fluxo.