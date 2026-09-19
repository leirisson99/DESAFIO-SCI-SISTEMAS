import pandas as pd
import json
from pathlib import Path
from ingestion.loader import preparation_conversation
from ingestion.insert_conversation import insert_conversation
from ingestion.embed_and_store import generation_embedding

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_PATH = BASE_DIR / "data" / "data" / "conversations.jsonl"

df = pd.read_json(DATA_PATH, lines=True)

# responsaavel por carregar o dataset
def load_conversations(path: str) -> list[dict]:
    conversation = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            conversation.append(json.loads(line))
    return conversation

def run_injestion():
    dataset = load_conversations(DATA_PATH)

    #contadores 
    inseridas = 0
    puladas = 0
    erros = 0
    total = 0

    # detecta se tem splits (DatasetDict) ou é uma lista única de conversas
    if hasattr (dataset, "keys"):
        conversas = []
        for split_name in dataset.keys():
            conversas.extend(dataset[split_name])
    else:
        conversas = dataset
    for conversa in conversas:
        total += 1

        prepared = preparation_conversation(conversa)

        text = prepared["text"]
        
        if not text:
            print(f"Pulando {prepared['id']} texto vazio.")
            puladas += 1
            continue

        vetor = generation_embedding(text)
        if vetor is None:
            print(f"Erro ao gerar embedding para a conversa: {conversa['id']}")
            erros +=1
            continue

        metadata = prepared.get("metadata", {})
        sucesso = insert_conversation(
            conversation_id=prepared["id"],
            content=text,
            embedding=vetor,
            intent= metadata.get("intent"),
            sector=metadata.get("sector"),
            sentiment=metadata.get("sentiment")
        )

        if sucesso:
            inseridas += 1
        else:
            erros += 1
        if total % 50 == 0:
            print(f"Progresso: {total} processadas...")

    print("\n--- Ingestão concluída ---")
    print(f"Total processado: {total}")
    print(f"Inseridas: {inseridas}")
    print(f"Puladas (vazias): {puladas}")
    print(f"Erros: {erros}")


if __name__ == "__main__":
    run_injestion()