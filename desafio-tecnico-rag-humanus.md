# Desafio Técnico — RAG com Strands Agents

## Objetivo

O objetivo deste desafio é desenvolver uma aplicação simples de **RAG (Retrieval-Augmented Generation)** utilizando **Python** e o framework **Strands Agents**.

A aplicação deverá utilizar uma base de conhecimento fornecida no desafio para buscar informações relevantes e responder às dúvidas do usuário com base no conteúdo encontrado.

> **Importante:** o foco deste desafio não é construir uma solução completa de produção. Queremos avaliar principalmente sua capacidade de estruturar uma solução de RAG, integrar as tecnologias escolhidas e explicar suas decisões.

---

## Desafio

Implemente um agente utilizando **Strands Agents** capaz de:

1. Receber uma pergunta do usuário;
2. Consultar uma base de conhecimento utilizando RAG;
3. Recuperar conteúdo relevante para a pergunta;
4. Utilizar o conteúdo recuperado como contexto para o modelo;
5. Retornar uma resposta ao usuário.

A forma de ingestão dos documentos, estratégia de chunking, embeddings, banco vetorial, modelo e arquitetura ficam a seu critério.

---

## Requisitos obrigatórios

- Utilizar **Python**;
- Utilizar o framework **Strands Agents**;
- Utilizar o dataset fornecido como base de conhecimento;
- Implementar algum mecanismo de busca/retrieval sobre o dataset;
- Gerar respostas utilizando o conteúdo recuperado da base de conhecimento;
- Disponibilizar instruções no `README.md` explicando como executar o projeto.

---

## Requisitos extras — opcionais

Os itens abaixo **não são obrigatórios**. Eles existem para que você possa explorar conhecimentos adicionais caso queira ir além da implementação básica.

- Hospedar/executar o agente utilizando **Amazon Bedrock AgentCore Runtime**;
- Implementar uma interface de **chat em Next.js** que se comunique com o agente;
- Implementar streaming das respostas no chat;
- Exibir no chat as fontes/documentos utilizados para gerar a resposta;
- Adicionar testes automatizados;
- Adicionar observabilidade, tracing ou métricas;
- Implementar qualquer outra melhoria que considere relevante para a solução.

Caso implemente algum extra, descreva brevemente no `README.md` o que foi feito e a motivação da escolha.

---

## Banco / Vector Store

A escolha da tecnologia para armazenamento e busca fica a seu critério.

Algumas opções possíveis:

- PostgreSQL + pgvector;
- Qdrant;
- Amazon S3 Vectors;
- Outra solução de sua preferência.

Não existe uma tecnologia obrigatória. Esperamos apenas que a escolha seja adequada para o desafio e esteja brevemente justificada no `README.md`.

---

## Modelo / LLM

A escolha do modelo e do provedor também fica a seu critério.

Exemplos:

- Groq;
- OpenAI;
- Amazon Bedrock;
- Outro modelo/provedor compatível com a solução.

Da mesma forma, você pode escolher livremente o modelo de embeddings utilizado para indexar e consultar os documentos.

---

## Dataset

Para o desafio, utilize o dataset **Brazilian Customer Service Conversations**, disponível no Hugging Face:

https://huggingface.co/datasets/RichardSakaguchiMS/brazilian-customer-service-conversations

O dataset contém conversas em português relacionadas a cenários de atendimento ao cliente em diferentes setores.

O candidato deverá utilizar esse conteúdo como base de conhecimento para a solução RAG, ficando livre para definir a estratégia de preparação, transformação, divisão e indexação dos dados.

A aplicação deve ser capaz de responder perguntas relacionadas ao conteúdo do dataset, mesmo quando a pergunta do usuário não estiver escrita exatamente da mesma forma que o conteúdo original.

Também é esperado um comportamento adequado quando a base de conhecimento **não possuir informação suficiente** para responder à pergunta.

---

## Entrega

O projeto deverá ser entregue em um repositório Git contendo, no mínimo:

- Código-fonte da solução;
- `README.md` com instruções para execução;
- Dependências necessárias;
- Configuração das variáveis de ambiente através de um `.env.example`, quando necessário;
- Breve descrição da arquitetura e das principais decisões técnicas.

**Não envie credenciais, tokens ou chaves de API no repositório.**

---

## O que será avaliado

A avaliação será feita principalmente sobre a implementação dos requisitos obrigatórios.

Serão observados:

- Funcionamento do fluxo de RAG;
- Qualidade da recuperação das informações da base de conhecimento;
- Uso adequado do Strands Agents;
- Organização e clareza do código;
- Estrutura da solução;
- Tratamento de erros e cenários sem resposta na base;
- Clareza da documentação;
- Capacidade de justificar as decisões técnicas adotadas.

Os requisitos extras serão considerados como **diferenciais**, mas sua ausência não prejudicará a avaliação dos requisitos obrigatórios.

---

## Documentação de referência

- Strands Agents: https://strandsagents.com

Você pode consultar documentações oficiais, bibliotecas, exemplos e outras referências durante o desenvolvimento.
