# outbound-leads

Projeto pessoal do Erick: outbound e extração de leads. Extrai e segmenta leads (clientes, parceiros e inteligência de concorrentes), dispara mensagens diretas aos poucos e mostra tudo num painel local.

Feito para agentes de IA: basta pedir "instale o outbound-leads e comece". O agente lê a skill, prepara o ambiente e conduz o fluxo.

## Instalar com IA

**Claude Code** (plugin com skill):

```
/plugin marketplace add erickmourasilva/outbound-leads
/plugin install outbound-leads@outbound-leads
```

Depois peça, por exemplo: "use o outbound-leads para extrair parceiros dos concorrentes e montar a fila".

**Outros agentes (Codex etc.):** clone o repositório e peça para ler `AGENTS.md`, que aponta para `skills/outbound-leads/SKILL.md`.

**Manual:**

```bash
git clone https://github.com/erickmourasilva/outbound-leads && cd outbound-leads
./setup.sh                  # verifica o ambiente e cria o banco local
python3 -m outbound serve   # painel em http://127.0.0.1:8787
```

Requisitos: Python 3.11+ (só biblioteca padrão). Para enviar mensagens, `agent-browser` (`npm install -g agent-browser`). Opcionais: pnpm e `portless` (URL `https://outbound-leads.localhost` com `pnpm dev`).

## Onde ficam os dados

`~/.outbound-leads` (mude com `OUTBOUND_HOME`): banco SQLite, exportações, importações e a sessão do navegador. Nada disso entra no git nem no código.

## Comandos (todos imprimem JSON)

| Comando | O que faz |
|---|---|
| `doctor` | Verifica o ambiente e diz o que corrigir |
| `import arquivo.csv` / `export` | Entrada e saída em CSV; deduplica por @ e respeita não contato |
| `leads list / add / set-status` | Gerenciar leads |
| `next` | Pode enviar agora? Retorna o motivo, o limite do dia e os próximos leads |
| `record-send <@> ok\|failed\|not_accepting\|blocked` | Registra um envio (`blocked` pausa tudo) |
| `pause` / `resume` | Chave geral; o envio começa pausado |
| `settings [chave valor]` | Limites do aquecimento e horários |
| `dnc <@>` | Não contatar, para sempre |
| `stats` | Contagens e previsão |
| `serve` | Painel local com atualização a cada 5 segundos |

Execute como `python3 -m outbound <comando>`. Formato do CSV: `kind,segment,name,handle,source_kind,source_ref,source_url,signal,signal_date,score,status` (`kind` = `client`, `partner` ou `intel`).

## Regras de envio (padrão)

- Aquecimento: 5 mensagens por dia na primeira semana, +5 por semana, teto de 30.
- Horário comercial (9h às 20h, Brasília), dias úteis, 90 a 240 segundos entre envios.
- Pausa total ao primeiro alerta, bloqueio ou erro da plataforma.
- Só envia com autorização do operador. A lista de não contato é permanente.
- Navegador sempre com janela visível; o operador faz o login. O projeto nunca digita senha nem código.
- Não simula comportamento humano para disfarçar automação e não contorna CAPTCHA nem bloqueios.

## Estrutura

```
.claude-plugin/        manifesto do plugin e do marketplace
skills/outbound-leads/ skill + referências (extração, mensagens, envio)
outbound/              pacote Python: db, schedule, forecast, dashboard, cli
sender/                protótipo supervisionado de envio (agent-browser)
tests/                 testes (unittest)
docs/                  plano e exemplos
AGENTS.md  setup.sh    entrada para agentes e setup idempotente
```

## Licença

MIT. Veja `LICENSE`.

## Aviso

Envio automatizado de mensagens pode violar os termos de uso da plataforma e restringir a conta. Mantenha volume baixo, aumente aos poucos e use uma conta própria para essa operação. Prospecção B2B deve respeitar a LGPD: abordar empresas com base em informação pública e profissional, e atender de imediato qualquer pedido para parar.
