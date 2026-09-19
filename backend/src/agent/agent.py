import os
from dotenv import load_dotenv
from strands import Agent
from strands.models.openai import OpenAIModel

from agent.tools import seek_knowledge, ultimos_resultados_var
from agent.prompts import SYSTEM_PROMPT

load_dotenv()


model = OpenAIModel(
    client_args = {"api_key" : os.getenv("OPENAI_API_KEY")},
    model_id= os.getenv("MODEL", "gpt-4o-mini")
)




def ask(question: str) -> str:
    """Envia uma pergunta ao agente e devolve a resposta como texto.
    Em caso de falha (API, rede, etc.), devolve uma mensagem amigável ao usuário
    e registra o erro real para depuração.
    """
    if not question or not question.strip():
         ultimos_resultados_var.set([])
         return "Por favor, envie uma pergunta para que eu possa ajudar."
     
    try:
        agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            tools=[seek_knowledge],
        )
        response = agent(question)
        ultimos_resultados_var.set(agent.state.get("ultimos_resultados") or [])
        return str(response)
    except Exception as e:
        ultimos_resultados_var.set([])
        print(f"[ERRO] Falha ao processar pergunta '{question}': {e}")
        return "Desculpe, ocorreu um problema ao processar sua pergunta. Tente novamente em instantes."


