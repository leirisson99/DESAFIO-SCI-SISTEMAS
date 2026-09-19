from retrival.search import search_similarit_conversation
if __name__ == "__main__":
    perguntas_teste = [
        "meu pedido não chegou, o que faço?",           # já testamos, serve de referência
        "cadê minha encomenda? já paguei e nada",        # paráfrase da primeira, com vocabulário bem diferente
        "quero cancelar meu plano de internet",          # tema diferente, mais direto
        "vc tem promoção de notebook?",                  # tema diferente, mais direto
        "qual a capital da França?",                     # totalmente fora do domínio
        "como faço um bolo de chocolate?",               # totalmente fora do domínio
    ]

    for pergunta in perguntas_teste:
        print(f"=== Pergunta: {pergunta} ===")
        resultados = search_similarit_conversation(pergunta)
        for r in resultados:
            print(f"[{r['similarity']:.3f}] {r['conversation_id']} ({r['intent']})")
            print(r['content'][:100], "...")
        print()