#!/usr/bin/env python3
"""
Gerador de conversas de atendimento ao cliente em PT-BR
Usa NVIDIA API (ou OpenAI) para gerar conversas sinteticas
"""

import json
import os
import random
import time
from pathlib import Path
from typing import Optional
import requests

# Configuracao
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OUTPUT_DIR = Path(__file__).parent.parent / "data"

# Categorias
SECTORS = [
    "ecommerce",
    "financeiro",
    "telecom",
    "saude",
    "educacao",
    "restaurante",
    "imobiliario",
    "tecnologia"
]

INTENTS = [
    "saudacao",
    "duvida_produto",
    "duvida_servico",
    "reclamacao",
    "suporte_tecnico",
    "compra",
    "cancelamento",
    "elogio",
    "outros"
]

SENTIMENTS = ["positive", "neutral", "negative"]

# Exemplos de contexto por setor
SECTOR_CONTEXT = {
    "ecommerce": "loja online que vende eletronicos, roupas e acessorios",
    "financeiro": "banco digital ou fintech com conta corrente e cartao",
    "telecom": "operadora de celular e internet banda larga",
    "saude": "clinica medica ou plano de saude",
    "educacao": "escola de idiomas ou curso online",
    "restaurante": "restaurante com delivery via app",
    "imobiliario": "imobiliaria que vende e aluga imoveis",
    "tecnologia": "empresa de software SaaS ou suporte tecnico"
}


def generate_prompt(sector: str, intent: str, sentiment: str) -> str:
    """Gera o prompt para a LLM"""
    context = SECTOR_CONTEXT.get(sector, "empresa generica")

    sentiment_guide = {
        "positive": "O cliente esta satisfeito e amigavel",
        "neutral": "O cliente esta neutro, apenas buscando informacao",
        "negative": "O cliente esta frustrado ou insatisfeito"
    }

    intent_guide = {
        "saudacao": "O cliente apenas cumprimenta e inicia conversa",
        "duvida_produto": "O cliente pergunta sobre caracteristicas, preco ou disponibilidade de produto",
        "duvida_servico": "O cliente pergunta sobre como funciona um servico, prazos ou processos",
        "reclamacao": "O cliente reclama de um problema que teve",
        "suporte_tecnico": "O cliente precisa de ajuda tecnica para resolver um problema",
        "compra": "O cliente quer fazer uma compra ou contratar servico",
        "cancelamento": "O cliente quer cancelar um servico ou devolucao",
        "elogio": "O cliente elogia o atendimento ou produto",
        "outros": "Conversa generica que nao se encaixa nas outras categorias"
    }

    return f"""Gere uma conversa realista de atendimento ao cliente em portugues brasileiro.

CONTEXTO:
- Empresa: {context}
- Setor: {sector}
- Intencao do cliente: {intent} - {intent_guide.get(intent, '')}
- Sentimento: {sentiment} - {sentiment_guide.get(sentiment, '')}

REQUISITOS:
1. Use portugues brasileiro natural (pode incluir girias leves como "beleza", "show", "ta bom")
2. Inclua erros de digitacao OCASIONAIS do cliente (tipo "vc" em vez de "voce", "td" em vez de "tudo")
3. O atendente deve ser profissional mas amigavel
4. A conversa deve ter entre 4 e 8 turnos (mensagens alternadas)
5. Resolva ou encaminhe o problema de forma realista
6. NAO use emojis excessivos

FORMATO DE SAIDA (JSON valido):
{{
  "messages": [
    {{"role": "customer", "content": "mensagem do cliente"}},
    {{"role": "agent", "content": "resposta do atendente"}},
    {{"role": "customer", "content": "..."}},
    {{"role": "agent", "content": "..."}}
  ]
}}

Gere APENAS o JSON, sem explicacoes adicionais."""


def call_nvidia_api(prompt: str) -> Optional[dict]:
    """Chama a API da NVIDIA"""
    if not NVIDIA_API_KEY:
        return None

    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta/llama-3.3-70b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "max_tokens": 1024
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        # Extrair JSON do conteudo
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
    except Exception as e:
        print(f"Erro NVIDIA API: {e}")

    return None


def call_openai_api(prompt: str) -> Optional[dict]:
    """Chama a API da OpenAI"""
    if not OPENAI_API_KEY:
        return None

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        print(f"Erro OpenAI API: {e}")

    return None


def generate_conversation(sector: str, intent: str, sentiment: str, conv_id: int) -> Optional[dict]:
    """Gera uma conversa completa"""
    prompt = generate_prompt(sector, intent, sentiment)

    # Tenta NVIDIA primeiro, depois OpenAI
    result = call_nvidia_api(prompt)
    if not result:
        result = call_openai_api(prompt)

    if not result or "messages" not in result:
        return None

    # Adiciona metadata
    result["id"] = f"conv_{conv_id:05d}"
    result["metadata"] = {
        "intent": intent,
        "sentiment": sentiment,
        "sector": sector,
        "turns": len(result["messages"]),
        "generated": True,
        "generator": "nvidia" if NVIDIA_API_KEY else "openai"
    }

    return result


def generate_dataset(total: int = 100, output_file: str = "conversations.jsonl"):
    """Gera o dataset completo"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_file

    # Calcular quantas conversas por combinacao
    combinations = []
    for sector in SECTORS:
        for intent in INTENTS:
            for sentiment in SENTIMENTS:
                combinations.append((sector, intent, sentiment))

    per_combo = max(1, total // len(combinations))

    print(f"Gerando {total} conversas...")
    print(f"Combinacoes: {len(combinations)}")
    print(f"Por combinacao: {per_combo}")
    print(f"API: {'NVIDIA' if NVIDIA_API_KEY else 'OpenAI' if OPENAI_API_KEY else 'NENHUMA'}")
    print("-" * 50)

    if not NVIDIA_API_KEY and not OPENAI_API_KEY:
        print("ERRO: Configure NVIDIA_API_KEY ou OPENAI_API_KEY")
        print("export NVIDIA_API_KEY='sua-chave'")
        print("export OPENAI_API_KEY='sua-chave'")
        return

    generated = 0
    errors = 0

    with open(output_path, "w", encoding="utf-8") as f:
        for i, (sector, intent, sentiment) in enumerate(combinations):
            for j in range(per_combo):
                if generated >= total:
                    break

                conv = generate_conversation(sector, intent, sentiment, generated)

                if conv:
                    f.write(json.dumps(conv, ensure_ascii=False) + "\n")
                    generated += 1
                    print(f"[{generated}/{total}] {sector}/{intent}/{sentiment} - OK")
                else:
                    errors += 1
                    print(f"[ERRO] {sector}/{intent}/{sentiment}")

                # Rate limiting
                time.sleep(0.5)

            if generated >= total:
                break

    print("-" * 50)
    print(f"Concluido! Geradas: {generated}, Erros: {errors}")
    print(f"Arquivo: {output_path}")


def split_dataset(input_file: str = "conversations.jsonl"):
    """Divide o dataset em train/validation/test"""
    input_path = OUTPUT_DIR / input_file

    if not input_path.exists():
        print(f"Arquivo nao encontrado: {input_path}")
        return

    # Ler todas as conversas
    with open(input_path, "r", encoding="utf-8") as f:
        conversations = [json.loads(line) for line in f]

    # Embaralhar
    random.shuffle(conversations)

    # Split 80/10/10
    total = len(conversations)
    train_end = int(total * 0.8)
    val_end = int(total * 0.9)

    train = conversations[:train_end]
    val = conversations[train_end:val_end]
    test = conversations[val_end:]

    # Salvar
    for name, data in [("train", train), ("validation", val), ("test", test)]:
        path = OUTPUT_DIR / f"{name}.jsonl"
        with open(path, "w", encoding="utf-8") as f:
            for conv in data:
                f.write(json.dumps(conv, ensure_ascii=False) + "\n")
        print(f"{name}: {len(data)} conversas -> {path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "split":
            split_dataset()
        elif sys.argv[1].isdigit():
            generate_dataset(total=int(sys.argv[1]))
        else:
            print("Uso: python generate.py [numero_de_conversas|split]")
    else:
        # Padrao: gerar 100 conversas de teste
        generate_dataset(total=100)
