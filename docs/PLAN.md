# Plano

Projeto pessoal do Erick de outbound e extração de leads.

## Objetivo

Extrair antes, segmentar, e só então enviar aos poucos. Acompanhar a lista e os disparos em tempo real e saber a previsão de término.

## O que fica de fora

CRM, funis, caixa de entrada e atendimento. Depois que o contato responde, a conversa segue no sistema que já cuida disso. Como a plataforma só permite que a pessoa responda depois de receber a primeira mensagem, o primeiro contato sai pelo navegador.

## Fases

0. **Agente (feito):** plugin do Claude Code com skill, `AGENTS.md`, `setup.sh`, `doctor` e comandos em JSON, para o agente instalar e usar sozinho.
1. **Base (feito):** banco SQLite, painel local, previsão, importação e exportação CSV, lista de não contato, testes.
2. **Extração:** diretórios públicos de parceiros de empresas concorrentes e, depois, listas de seguidores de perfis concorrentes, em ritmo baixo, filtrando só contas comerciais. O @ sempre vem de fonte verificável.
3. **Segmentação e pontuação:** por tipo (cliente, parceiro, concorrente), segmento e sinal público; fila diária visível no painel.
4. **Envio:** worker com limites, janelas de horário, aquecimento, pausa por alerta e captura de tela em falha. Hoje existe só o protótipo supervisionado em `sender/`.
5. **Medição:** variantes de texto (A/B, uma variável por vez) e atribuição por etiqueta no CRM. Respostas e conversões ficam no CRM; o painel pode importar um CSV de exportação para estimar a taxa de resposta.
6. **Piloto e escala:** 5 por dia, aumento semanal, só com autorização explícita do operador.

## Decisões

- Armazenamento: SQLite local como fonte única; CSV para entrada e saída.
- Navegador: `agent-browser` com janela visível; o login é feito pelo operador.
- Painel: servidor só em `127.0.0.1`, URL estável via `portless`; alterações só com cabeçalho `X-Requested-With`.
- Afirmações nas mensagens: só as comprovadas em material público do produto.
- Dados de leads, textos e perfis contatados ficam em arquivos locais, nunca no código.

## Riscos

- Violação dos termos da plataforma por automação (envio e leitura de seguidores). Mitigação: volume baixo, janela visível, pausa ao primeiro alerta, conta dedicada.
- Contas que não aceitam solicitações de contato: a mensagem pode não ser entregue.
- LGPD: usar apenas informação pública e profissional; não coletar telefone nem e-mail pessoal; não tratar dados sensíveis.
- Dados de leads ficam fora do git (`data/`, `imports/`, `exports/`).
