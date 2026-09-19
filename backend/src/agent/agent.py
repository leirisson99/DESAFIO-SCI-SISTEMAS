import os
from dotenv import load_dotenv
from strands import Agent
from strands.models.openai import OpenAIModel

from agent.tools import seek_knowledge
from agent.prompts import SYSTEM_PROMPT

load_dotenv()


model = OpenAIModel(
    client_args = {"api_key" : os.getenv("OPENAI_API_KEY")},
    model_id= os.getenv("MODEL", "gpt-4o-mini")
)

agent = Agent(
    model=model,
    system_prompt = SYSTEM_PROMPT,
    tools=[seek_knowledge]
)


def ask(question: str) -> str:
    """Envia uma pergunta ao agente e devolve a resposta como texto."""
    response = agent(question)
    return str(response)

if __name__ == "__main__":
    pergunta = "qual a capital da França?"
    print(f"Pergunta: {pergunta}\n")
    resposta = ask(pergunta)
    print(f"Resposta: {resposta}")