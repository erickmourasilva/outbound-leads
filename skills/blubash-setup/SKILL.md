---
name: blubash-setup
description: >-
  Configura a BluBash (CRM com agentes de IA e pipelines) para atender, qualificar
  e levar ao funil os leads que respondem às DMs do outbound no Instagram. Cria a
  conta (login com Google), o workspace, o agente de IA de vendas, o treinamento,
  as habilidades, o pipeline e conecta o Instagram, tudo guiado pelo navegador. O
  usuário só entra nos logins e validações. Use quando o outbound-leads pedir para
  configurar as respostas, quando o usuário disser "configurar a BluBash",
  "criar a conta na BluBash", "criar o agente de atendimento", "conectar o
  Instagram na BluBash", ou quando `python3 -m outbound replies` ou `next`
  indicarem que as respostas ainda não têm destino.
---

# blubash-setup

O outbound **abre** a conversa. A BluBash **fecha**: atende quem responde na hora, qualifica, agenda, cobra e move o negócio no pipeline, e passa para a equipe com todo o contexto. Esta skill monta isso de ponta a ponta, ao vivo, na frente do usuário.

> **Sem este setup o envio não é liberado.** O `outbound-leads` só envia quando as respostas têm destino. O caminho mais rápido, já encaixado e plug and play, é este.

Tudo aqui vem de fontes públicas: https://blubash.io e https://docs.blubash.io. Nada é inventado: se uma tela divergir do guia, leia a tela (`snapshot`) e use a documentação.

## Como conduzir

1. Rode `python3 -m outbound blubash next`. Ele diz a etapa atual, quem age e o que pedir ao usuário.
2. Execute a etapa pelo navegador, sempre **com janela visível**: `agent-browser --headed --session blubash-setup --session-name blubash-setup open <url>`. Use `snapshot -i` para achar os botões pelo nome na tela.
3. Ao terminar e **confirmar na tela**, registre: `python3 -m outbound blubash done <etapa>`. Repita até `ready: true`.
4. Comece apresentando em duas frases o que vai acontecer e que o usuário só será chamado nos logins e validações. Não peça permissão a cada clique.

Etapas (detalhes em `references/runbook.md`): `account` → `workspace` → `brief` → `crm_base` → `agent` → `training` → `skills` → `test` → `channel` → `link` → `verify`. O envio é liberado depois de `link`.

## Quando parar e chamar o usuário

Sempre que a tela pedir algo que só ele pode dar. Diga em uma frase o que precisa e aguarde ("Preciso de você: ..."):

- **Login do Google** e o consentimento (etapa `account`).
- **Login do Instagram** e a autorização das permissões, com a conta que envia as DMs (etapa `channel`).
- **Qualquer** senha, código de verificação (2FA, e-mail), aceite de termos ou autorização OAuth.
- **Assinatura, plano, pagamento e dados fiscais.** Se a tela mostrar teste, limite ou cobrança, pare, explique e deixe o usuário decidir. Você nunca preenche cartão, CPF/CNPJ ou endereço.
- A DM de teste de outra conta (etapa `verify`).

Nunca digite credenciais, nunca contorne CAPTCHA ou bloqueio e nunca marque uma etapa como feita sem ver o resultado na tela.

## O que entregar ao final

`python3 -m outbound blubash status` com `ready: true`. Resuma ao usuário: conta, workspace, agente (nome e propósito), pipeline, canal Instagram conectado e o teste de ponta a ponta. Diga que agora o envio está liberado e que as respostas vão para o agente e para o funil.

## Referências

- `references/runbook.md`: o passo a passo de cada etapa, com o que o agente faz, o que o usuário faz e como verificar.
- `references/sales-agent.md`: as 6 perguntas, o modelo de Comportamento do agente de vendas, o treinamento e as habilidades.
- `references/troubleshooting.md`: popups, Instagram que não conecta ou não entrega, limites do plano, agente que não responde.
