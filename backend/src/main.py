
from datasets import load_dataset
from ingestion.loader import format_conversation
dataset = load_dataset("RichardSakaguchiMS/brazilian-customer-service-conversations")




for i in range(5):
    conversa = dataset["train"][i]
    print(f"---{conversa['id']}")
    print(format_conversation(conversa["messages"]))
    print()