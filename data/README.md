---
language:
- pt
license: apache-2.0
task_categories:
- text-classification
- question-answering
- text-generation
pretty_name: Brazilian Customer Service Conversations
size_categories:
- 1K<n<10K
tags:
- customer-service
- chatbot
- portuguese
- brazilian
- atendimento
- nlu
- intent-detection
- dialogue
- nlp
- sentiment-analysis
- intent-classification
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train.jsonl
  - split: validation
    path: data/validation.jsonl
  - split: test
    path: data/test.jsonl
---

# Brazilian Customer Service Conversations

Dataset de conversas de atendimento ao cliente em portugues brasileiro (PT-BR).

De um like me apoie em manter esse dataset!

## Descricao

Conversas sinteticas de alta qualidade simulando interacoes reais entre clientes e atendentes em diversos setores da economia brasileira. Util para treinar e avaliar modelos de:

- Chatbots de atendimento
- Classificacao de intencao (intent classification)
- Analise de sentimento em conversas
- Geracao de respostas contextuais

## Estatisticas

| Metrica | Valor |
|---------|-------|
| Total de conversas | 1.000+ |
| Total de mensagens | ~7.000 |
| Media de turnos | ~7 |
| Setores | 8 |
| Intencoes | 9 |
| Sentimentos | 3 |

## Setores

- E-commerce
- Financeiro (bancos, fintechs)
- Telecom
- Saude
- Educacao
- Restaurante/Delivery
- Imobiliario
- Tecnologia/SaaS

## Intencoes

| Intencao | Descricao |
|----------|-----------|
| saudacao | Cumprimento inicial |
| duvida_produto | Perguntas sobre produtos |
| duvida_servico | Perguntas sobre servicos |
| reclamacao | Problema ou insatisfacao |
| suporte_tecnico | Ajuda tecnica |
| compra | Intencao de comprar |
| cancelamento | Pedido de cancelamento |
| elogio | Feedback positivo |
| outros | Outras situacoes |

## Sentimentos

- `positive`: Cliente satisfeito
- `neutral`: Cliente neutro
- `negative`: Cliente insatisfeito

## Estrutura dos Dados

```json
{
  "id": "conv_00042",
  "messages": [
    {"role": "customer", "content": "Oi, preciso de ajuda"},
    {"role": "agent", "content": "Ola! Como posso ajudar?"}
  ],
  "metadata": {
    "intent": "duvida_servico",
    "sentiment": "neutral",
    "sector": "ecommerce",
    "turns": 2
  }
}
```

## Uso

### Carregar dataset

```python
from datasets import load_dataset

dataset = load_dataset("RichardSakaguchiMS/brazilian-customer-service-conversations")

train = dataset["train"]
validation = dataset["validation"]
test = dataset["test"]
```

### Classificacao de intencao

```python
X = [ex["messages"][0]["content"] for ex in dataset["train"]]
y = [ex["metadata"]["intent"] for ex in dataset["train"]]
```

### Analise de sentimento

```python
texts = [" ".join([m["content"] for m in ex["messages"]]) for ex in dataset["train"]]
labels = [ex["metadata"]["sentiment"] for ex in dataset["train"]]
```

## Caracteristicas linguisticas

O dataset captura caracteristicas do portugues brasileiro informal:

- Abreviacoes: vc, td, ta, pq, msg
- Girias: beleza, show, blz
- Informalidade controlada
- Variacao de registro

## Benchmark

| Tarefa | Metrica | Baseline |
|--------|---------|----------|
| Intent Classification | F1-Score | ~0.72 |
| Sentiment Analysis | Accuracy | ~0.78 |

## Limitacoes

- Dataset sintetico (gerado por LLM)
- Pode conter vieses do modelo gerador
- Recomenda-se complementar com dados reais para producao

## Licenca

Apache 2.0

## Citacao

```bibtex
@dataset{sakaguchi2025brazilian,
  author = {Richard Sakaguchi},
  title = {Brazilian Customer Service Conversations},
  year = {2025},
  publisher = {Hugging Face},
  url = {https://huggingface.co/datasets/RichardSakaguchiMS/brazilian-customer-service-conversations}
}
```

## Autor

Richard Sakaguchi - [sakaguchi.ia.br](https://sakaguchi.ia.br)
