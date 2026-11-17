# Runbook: BluBash do zero ao primeiro lead atendido

App e cadastro: pegue os endereços em `python3 -m outbound blubash status` (campos `app` e `signup`; por padrão `https://app.blubash.io`, ajustável com a variável `BLUBASH_APP_URL` para homologação). Documentação: https://docs.blubash.io/pt-BR

Para cada etapa: **Agente** é o que você faz, **Usuário** é o que só ele faz, **Verificar** é a prova na tela antes de rodar `python3 -m outbound blubash done <etapa>`. Os nomes de botões vêm da interface em português; se mudarem, use o que o `snapshot` mostrar.

## 1. `account`: criar a conta

- **Agente:** abra o endereço `signup` do `blubash status` (se já houver login, o app abre direto: verifique e pule). Clique em **Cadastrar com Google**.
- **Usuário:** escolher a conta Google e autorizar na janela do Google. Peça: "Preciso de você: escolha sua conta Google e autorize. Me avise quando o app abrir."
- O Google abre **na mesma aba** (é um redirecionamento, não um pop-up). Depois do consentimento o navegador passa por um endereço de retorno (`.../auth/callback`) e volta sozinho ao app, então a URL intermediária não é critério.
- O Google pode abrir o campo **E-mail ou telefone** ou a lista **Escolha uma conta** (se já houver contas no navegador). As duas são do usuário: não clique nem digite por ele.
- Depois do consentimento, aguarde o retorno (`wait 3000`) antes de ler a tela com `snapshot -i`: logo após o redirecionamento a página ainda está carregando.
- **Verificar:** o app mostra a **navegação lateral** (Dashboard, Conversas...) ou o assistente inicial de criação do workspace. Se continuar na tela do Google ou de login, a etapa não terminou.
- Alternativa só se o usuário preferir: formulário com nome, e-mail e senha. Quem digita senha e confirma o e-mail é o usuário.

## 2. `workspace`: criar o workspace

- **Agente:** se o app pedir para criar ou escolher um workspace, escolha **criar um novo** e use o nome da empresa (se ainda não tiver, pergunte só o nome da empresa). Confirme.
- **Verificar:** o Dashboard abre com o nome do workspace. A faixa de **teste de 7 dias** é esperada: ignore ou feche e siga. Não clique em ativar assinatura.

## 3. `brief`: dados da empresa

- **Agente:** faça as 7 perguntas de `sales-agent.md`, uma mensagem só, e grave cada resposta: `python3 -m outbound blubash brief company="..." offer="..." ...`.
- **Verificar:** `python3 -m outbound blubash brief` sem itens em `missing` (o `faq` pode ser o site).

## 4. `crm_base`: equipe, etiquetas e pipeline

Documentação: `pt-BR/pipelines/create-pipeline`, `pt-BR/account-settings/create-tags`.

- **Agente:**
  1. Confirme que existe uma **equipe** (a do workspace serve) e anote o nome: ela será a Equipe Padrão do canal e o destino das transferências.
  2. Em **Etiquetas**, crie: `outbound`, `outbound-interessado`, `outbound-quente`, `nao-contatar`.
  3. Em **Pipelines** → **Novo pipeline**, escolha o **modelo Vendas**, dê o nome (ex.: "Outbound") e vincule à equipe. Mantenha as etapas e os **motivos de Ganho e de Perda** do modelo. **Anote os nomes reais** da primeira etapa, da etapa de qualificação e dos motivos de perda: o Comportamento do agente vai usá-los.
- **Verificar:** etiquetas e pipeline aparecem nas listas, com etapas de Ganho e de Perdido e motivos cadastrados.

## 5. `agent`: criar o agente de vendas

Documentação: `pt-BR/ai-agents/create-ai-agent`. É preciso ser **Administrador**.

- **Agente:** menu **Agentes de IA** → **Criar Agente**.
  - **Perfil:** Nome do Agente (um nome humano e curto, definido com o usuário), **Propósito: Vendas** (use *Geração de Leads* só se o usuário não vender nada direto), **Tom: Normal** (ou o do `brief`), **Comportamento** = o modelo de `sales-agent.md` já preenchido (até 5.000 caracteres).
  - **Empresa:** nome e descrição (oferta em poucas linhas, serviços e horário de atendimento).
  - **Revisão:** confira e clique em **Criar**.
- **Verificar:** aviso de sucesso e a página do agente aberta. Se o limite de agentes do plano for atingido, pare e chame o usuário.

## 6. `training`: conhecimento

Documentação: `pt-BR/ai-agents/train-ai-agent`.

- **Agente:** na aba de treinamentos adicione, como texto, blocos separados por assunto: (1) produto e oferta, (2) perguntas frequentes e objeções reais, (3) o que NÃO pode ser prometido (preço, prazo, garantia). Se houver site, adicione a URL.
- **Verificar:** todos os itens chegam ao estado **Treinado**. Se algum falhar, remova e adicione de novo.
- Regras de decisão (quando transferir, quando etiquetar) ficam no **Comportamento**, não só no treinamento.

## 7. `skills`: habilidades

Documentação: `pt-BR/ai-agents/configure-skills`.

- **Agente:** na aba de habilidades, adicione e **dê um nome claro e descritivo** a cada uma, com orientação curta de quando usar e quando não usar:
  - uma de **adicionar etiqueta** para cada etiqueta (interessado, quente, não contatar);
  - **transferir para equipe**, apontando para a equipe comercial, que precisa ter acesso ao canal do Instagram;
  - **gerenciar negócios**, com o pipeline de vendas, todas as etapas em aberto liberadas para criar e mover, e **permitindo ganho e perda**: o agente fecha como **Perdido** quem for desqualificado e como **Ganho** só quando a condição de ganho do `brief` acontecer (regras no Comportamento);
  - manter ativas a nota interna e a atualização de contato.
- **Verificar:** as habilidades listadas e salvas.

## 8. `test`: testar

Documentação: `pt-BR/ai-agents/test-ai-agent`.

- **Agente:** em **Testar Agente**, rode estes cenários e leia as respostas: (1) "oi, vi sua mensagem, do que se trata?"; (2) pergunta de preço; (3) "já uso outra ferramenta"; (4) "agora não"; (5) "pare de me mandar mensagem"; (6) um lead claramente fora do perfil; (7) um lead que aceita avançar. Ajuste o Comportamento se o agente inventar algo, fizer várias perguntas de uma vez ou ignorar um pedido para parar.
- **Verificar:** os sete cenários com resposta curta, correta e dentro dos limites, e com o negócio sendo perdido ou ganho nos casos certos (no teste as ações aparecem como simuladas).

## 9. `channel`: conectar o Instagram

Documentação: `pt-BR/channels/configure-instagram`. Precisa de conta **profissional** do Instagram, e deve ser a **mesma conta que envia as DMs**: as respostas chegam ao Direct dela.

- **Agente:** **Canais** → **Adicionar Canal** → **Instagram**. Informe o nome do canal e a **Equipe Padrão**. Clique em **Criar Canal** e depois em **Conectar com Instagram**. Libere pop-ups se o navegador bloquear.
- **Usuário:** na janela do Instagram, fazer login e autorizar. Peça: "Preciso de você: entre no Instagram com a conta que envia as DMs e autorize."
- **Verificar:** "Instagram conectado com sucesso", selo **Conectado** e o nome de usuário igual ao da conta que envia.

## 10. `link`: ativar e vincular

Documentação: `pt-BR/ai-agents/activate-deactivate-agent`.

- **Agente:** em **Agentes de IA**, ative o agente. Em **Canais** → Instagram → Configurações do Canal, selecione o agente em **Agente de IA** e **Salvar**.
- **Verificar:** o agente aparece como **Ativo** e selecionado no canal. A partir daqui o envio do outbound é liberado.

## 11. `verify`: teste de ponta a ponta

- **Usuário:** enviar uma DM de **outra** conta do Instagram para a conta conectada. Peça: "Preciso de você: mande uma DM de outra conta para a conta conectada."
- **Agente:** abra a caixa de entrada, confirme que a conversa apareceu, que há o aviso de **Agente de IA Ativo** e que a resposta segue o Comportamento. Anote se a conversa mostra ou não a sua mensagem original: o agente não deve depender dela.
- **Verificar:** rode `python3 -m outbound blubash done verify` e confirme `ready: true` em `blubash status`.
