from agent.agent import ask
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # backend/
RELATORIO_PATH = BASE_DIR / "tests" / "relatorio_testes.md"

RETRIEVAL_DIRETO = [
    ("meu pedido não chegou, o que faço?", "pedido atrasado / duvida_servico"),
    ("quero cancelar meu plano de internet", "cancelamento"),
    ("vc tem promoção de notebook?", "compra / desconto"),
    ("como funciona o delivery do app?", "duvida_servico (restaurante)"),
    ("vc tem algum imóvel para venda em São Paulo?", "compra (imobiliário)"),
    ("qual o preço do plano de internet?", "duvida_produto"),
    ("o lanche de frango ainda está disponível?", "duvida_produto (restaurante)"),
    ("oi, tudo bem?", "saudacao"),
    ("td show, adorei o atendimento de vocês", "elogio"),
    ("fiz uma compra com o cartão do banco, como confirmo?", "duvida_servico"),
    ("meu pedido está pago mas não recebi nenhuma atualização", "duvida_servico"),
    ("quero desconto em eletrônicos", "compra"),
]

PARAFRASES = [
    ("meu pedido não chegou, o que faço?", "cadê minha encomenda? já paguei e nada"),
    ("quero cancelar meu plano de internet", "não quero mais esse serviço de internet, como encerro?"),
    ("vc tem promoção de notebook?", "tá rolando algum desconto em laptop?"),
    ("como funciona o delivery do app?", "como que faz pra receber o pedido em casa?"),
    ("vc tem algum imóvel para venda em São Paulo?", "tem alguma casa ou apê à venda na capital paulista?"),
    ("qual o preço do plano de internet?", "quanto custa esse pacote de internet de vocês?"),
    ("o lanche de frango ainda está disponível?", "ainda dá pra pedir aquele sanduíche de galinha?"),
    ("oi, tudo bem?", "e aí, beleza?"),
    ("td show, adorei o atendimento de vocês", "mto bom o suporte de vcs, parabéns"),
    ("fiz uma compra com o cartão do banco, como confirmo?", "paguei no crédito, como sei se deu certo?"),
    ("meu pedido está pago mas não recebi nenhuma atualização", "já paguei td mas ninguém me avisou de nada sobre a entrega"),
    ("quero desconto em eletrônicos", "tem algum abatimento em produtos eletrônicos?"),
]

FORA_DOMINIO = [
    "qual a capital da França?",
    "como faço um bolo de chocolate?",
    "vocês vendem carros?",
    "qual o horário de funcionamento da loja física?",
    "qual é a previsão do tempo pra amanhã?",
    "vocês têm plano de saúde empresarial?",
    "como resolvo um bug no meu código Python?",
    "quem é o presidente do Brasil?",
]


def run_retrieval_direto() -> list[dict]:
    resultados = []
    for pergunta, esperado in RETRIEVAL_DIRETO:
        resposta = ask(pergunta)
        resultados.append({"pergunta": pergunta, "esperado": esperado, "resposta": resposta})
    return resultados


def run_parafrases() -> list[dict]:
    resultados = []
    for original, parafrase in PARAFRASES:
        resposta_original = ask(original)
        resposta_parafrase = ask(parafrase)
        resultados.append({
            "original": original,
            "resposta_original": resposta_original,
            "parafrase": parafrase,
            "resposta_parafrase": resposta_parafrase,
        })
    return resultados


def run_fora_dominio() -> list[dict]:
    resultados = []
    for pergunta in FORA_DOMINIO:
        resposta = ask(pergunta)
        resultados.append({"pergunta": pergunta, "resposta": resposta})
    return resultados




def gerar_relatorio(caminho: Path = RELATORIO_PATH):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("# Relatório de Testes — Fase 6\n\n")

        f.write("## 1. Retrieval Direto\n\n")
        for r in run_retrieval_direto():
            f.write(f"**Pergunta:** {r['pergunta']}\n\n")
            f.write(f"**Tema esperado:** {r['esperado']}\n\n")
            f.write(f"**Resposta obtida:** {r['resposta']}\n\n")
            f.write("---\n\n")

        f.write("## 2. Paráfrases\n\n")
        for r in run_parafrases():
            f.write(f"**Original:** {r['original']}\n\n")
            f.write(f"**Resposta (original):** {r['resposta_original']}\n\n")
            f.write(f"**Paráfrase:** {r['parafrase']}\n\n")
            f.write(f"**Resposta (paráfrase):** {r['resposta_parafrase']}\n\n")
            f.write("---\n\n")

        f.write("## 3. Fora do Domínio\n\n")
        for r in run_fora_dominio():
            f.write(f"**Pergunta:** {r['pergunta']}\n\n")
            f.write(f"**Resposta obtida:** {r['resposta']}\n\n")
            f.write("---\n\n")

    print(f"Relatório gerado em: {caminho}")


if __name__ == "__main__":
    gerar_relatorio()