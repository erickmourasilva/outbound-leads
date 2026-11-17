# Runbook: BluBash do zero ao primeiro lead atendido

App e cadastro: pegue os endereços em `python3 -m outbound blubash status` (campos `app` e `signup`; por padrão `https://app.blubash.io`, ajustável com a variável `BLUBASH_APP_URL` para homologação). Documentação: https://docs.blubash.io/pt-BR

Para cada etapa: **Agente** é o que você faz, **Usuário** é o que só ele faz, **Verificar** é a prova na tela antes de rodar `python3 -m outbound blubash done <etapa>`. Os nomes de botões vêm da interface em português; se mudarem, use o que o `snapshot` mostrar.

## 1. `brief`: dados da empresa (antes do navegador)

- **Agente:** faça, **numa única mensagem**, as perguntas de `sales-agent.md` (9 itens, incluindo o @ do Instagram e o nome do agente) e grave as respostas: `python3 -m outbound blubash brief company="..." offer="..." ...`.
- **Verificar:** `python3 -m outbound blubash brief` sem itens em `missing` (o `faq` pode ser o site).

## 2. `account`: criar a conta

- **Agente:** abra o endereço `signup` do `blubash status` (se já houver login, o app abre direto: verifique e pule). Clique em **Cadastrar com Google**.
- **Usuário:** escolher a conta Google e autorizar na janela do Google. Peça: "Preciso de você: escolha sua conta Google e autorize. Me avise quando o app abrir."
- O Google abre **na mesma aba** (é um redirecionamento, não um pop-up). Depois do consentimento o navegador passa por um endereço de retorno (`.../auth/callback`) e volta sozinho ao app, então a URL intermediária não é critério.
- O Google pode abrir o campo **E-mail ou telefone** ou a lista **Escolha uma conta** (se já houver contas no navegador). As duas são do usuário: não clique nem digite por ele.
- Depois do consentimento, aguarde o retorno (`wait 3000`) antes de ler a tela com `snapshot -i`: logo após o redirecionamento a página ainda está carregando.
- **Verificar:** o app mostra a **navegação lateral** (Dashboard, Conversas...) ou o assistente inicial de criação do workspace. Se continuar na tela do Google ou de login, a etapa não terminou.
- Alternativa só se o usuário preferir: formulário com nome, e-mail e senha. Quem digita senha e confirma o e-mail é o usuário.
- Confirme também que o login deu certo citando o nome ou o e-mail do usuário, se aparecerem no menu do perfil: a navegação lateral sozinha não prova isso.

## 3. `workspace`: criar o workspace

- **Agente:** se o app abrir direto num Dashboard ou numa lista de workspaces já existentes (conta que já foi usada), **crie um novo** pelo seletor de workspaces, e não use um existente, a menos que o usuário peça. Na tela **Criar Workspace** preencha só **Nome** (obrigatório: o nome da empresa do `brief`) e **Descrição** (a oferta em uma frase). A **URL do Logo** é opcional: deixe em branco. Confirme em **Criar**.
- **Verificar:** o Dashboard abre com o nome do novo workspace. A faixa de **teste de 7 dias** é esperada: ignore ou feche e siga. Não clique em ativar assinatura.

## 4. `crm_base`: equipe, etiquetas e pipeline

Documentação: `pt-BR/pipelines/create-pipeline`, `pt-BR/account-settings/create-tags`.

- **Agente:**
  1. Confirme que existe uma **equipe** (normalmente o workspace já vem com uma) e anote o nome: ela será a Equipe Padrão do canal e o destino das transferências.
  2. Em **Etiquetas**, crie as quatro abaixo, **cada uma com uma cor diferente**. O campo **Cor** é um texto hexadecimal (com uma amostra ao lado) e, por padrão, todas nascem iguais, o que atrapalha a leitura do funil. Se errar, edite depois pelo ícone de lápis. Confira na tela que ficaram visivelmente distintas:

     | Etiqueta | Cor | Hex | Significado |
     |---|---|---|---|
     | `outbound` | azul | `#3B82F6` | veio da abordagem ativa |
     | `outbound-interessado` | verde | `#22C55E` | demonstrou interesse real |
     | `outbound-quente` | laranja | `#F97316` | perfil A, pronto para a equipe |
     | `nao-contatar` | vermelho | `#EF4444` | pediu para parar |

  3. Em **Pipelines** → **Novo pipeline** (um assistente em passos: modelo, nome e campos, equipe, etapas, motivos e a revisão "Pronto para criar"), escolha o **modelo Vendas**, dê o nome (ex.: "Outbound") e vincule à equipe. Mantenha as etapas e os motivos do modelo e **acrescente** o motivo de perda que corresponde à perda do `brief` (ex.: "Sem interesse"), se ele não existir: o agente só pode usar motivos que estejam cadastrados. Clique em **Criar pipeline**. **Anote os nomes reais** da primeira etapa, da etapa de qualificação e dos motivos de perda: o Comportamento do agente vai usá-los.
- **Verificar:** as quatro etiquetas aparecem com cores diferentes, e o pipeline com etapas de Ganho e de Perdido e os motivos cadastrados.

## 5. `agent`: criar o agente de vendas

Documentação: `pt-BR/ai-agents/create-ai-agent`. É preciso ser **Administrador**.

- **Agente:** menu **Agentes de IA** → **Criar Agente**, um assistente de 3 passos.
  - **Perfil:** Nome do Agente (o `agent_name` do `brief`); **Propósito** e **Tom** são seletores: clique no seletor e depois na opção, sem usar `fill`. Propósito **Vendas** (use *Geração de Leads* só se o usuário não vender nada direto); Tom conforme o `brief`; **Comportamento** = o modelo de `sales-agent.md` já preenchido (até 5.000 caracteres; `fill` funciona, inclusive com várias linhas).
  - **Empresa:** Nome da Empresa e Descrição da Empresa (oferta em poucas linhas, serviços, horário de atendimento e site).
  - **Revisão:** confira e clique em **Criar**.
  - O botão **Próximo** (e o **Criar**) fica abaixo de um campo grande: use `scrollintoview @ref` antes do `click`. Sem isso o clique não faz nada e **não dá erro**: confira sempre que a tela avançou.
- **Verificar:** aviso de sucesso e a página do agente aberta. Se o limite de agentes do plano for atingido, pare e chame o usuário.

## 6. `training`: conhecimento

Documentação: `pt-BR/ai-agents/train-ai-agent`.

- **Agente:** na aba de treinamentos adicione, em **Adicionar texto**, blocos separados por assunto: (1) produto e oferta, (2) perguntas frequentes e objeções reais, (3) o que NÃO pode ser prometido (preço, prazo, garantia, desconto). Se houver site, use **Adicionar site** com a URL: ele fica em "Processando" por cerca de 30 segundos ou mais.
- Se o usuário só deu o **site** como resposta da pergunta de conhecimento, o bloco de perguntas e objeções fica genérico: escreva-o a partir do que o site mostra e avise o usuário que vale complementar depois com as perguntas reais dos clientes.
- **Verificar:** todos os itens chegam ao estado **Treinado**. Se algum falhar, remova e adicione de novo.
- Regras de decisão (quando transferir, quando etiquetar) ficam no **Comportamento**, não só no treinamento.

## 7. `skills`: habilidades

Documentação: `pt-BR/ai-agents/configure-skills`.

- Algumas habilidades já vêm: **Adicionar nota** e **Transferir para humano** são nativas e sempre ativas; **Atualizar contato** e **Encerrar conversa** têm interruptor (deixe **Atualizar contato** ligada).
- **Agente:** na aba de habilidades use **Adicionar habilidade**. Os tipos são: Adicionar etiqueta, Remover etiqueta, Transferir para equipe, Transferir para agente IA, Enviar mídia e Gerenciar negócios. O **nome vem pré-preenchido com o tipo: troque por um nome claro e descritivo**, e escreva uma orientação curta de quando usar e quando não usar.
  - Uma de **Adicionar etiqueta** para cada etiqueta (interessado, quente, não contatar).
  - **Transferir para equipe**, apontando para a equipe comercial, que precisa ter acesso ao canal do Instagram.
  - **Gerenciar negócios**: escolha o pipeline. Aparecem então **Etapas em aberto** (seleção múltipla: marque todas as abertas), as ações (criar, mover, atualizar campos, nota, tarefa) e os interruptores **Permitir ganho** e **Permitir perda**: **ligue os dois**. O agente fecha como **Perdido** quem for desqualificado e como **Ganho** só quando a condição de ganho do `brief` acontecer (regras no Comportamento).
- Depois de abrir um diálogo ou mudar de passo, os `@ref` mudam: refaça o `snapshot -i` antes de cada clique.
- **Verificar:** as habilidades listadas e salvas.

## 8. `test`: testar

Documentação: `pt-BR/ai-agents/test-ai-agent`.

- **Agente:** em **Testar Agente**, rode estes cenários e leia as respostas: (1) "oi, vi sua mensagem, do que se trata?"; (2) pergunta de preço; (3) "já uso outra ferramenta"; (4) "agora não"; (5) "pare de me mandar mensagem"; (6) um lead claramente fora do perfil; (7) um lead que aceita avançar. Ajuste o Comportamento se o agente inventar algo, fizer várias perguntas de uma vez ou ignorar um pedido para parar.
- **Se o campo "Digite sua mensagem..." ficar desabilitado ou a tela falhar:** feche o painel (para parar as tentativas), **pare e chame o usuário**. Não marque a etapa como feita nem pule sozinho. O usuário pode autorizar a seguir sem o teste e voltar a ele depois do canal; o envio não depende desta etapa.
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
