# outbound-leads

Projeto pessoal do Erick: outbound e extração de leads. Extrai e segmenta leads (clientes, parceiros e inteligência de concorrentes), dispara mensagens diretas aos poucos e mostra tudo num painel local.

**Escopo:** só a parte ativa. Encontrar quem abordar (clientes, parceiros e inteligência de concorrentes), segmentar, enviar aos poucos e acompanhar. Quando a pessoa responde, a conversa segue em outro sistema (o CRM e o time de atendimento). Nada disso é reimplementado aqui.

## Como rodar

Requisitos: Python 3.11+ (só biblioteca padrão), Node 22+ e pnpm. O `portless` é instalado como dependência de desenvolvimento.

```bash
pnpm install
pnpm db:init          # cria data/outbound.db
pnpm db:seed          # importa leads já contatados de data/seed_leads.json (local, fora do git; veja docs/examples)
pnpm dev              # painel em https://outbound-leads.localhost (via portless)
pnpm test             # testes
```

Sem o `portless`: `pnpm serve` (porta 8787, só em `127.0.0.1`).

| Comando | O que faz |
|---|---|
| `pnpm leads:import imports/arquivo.csv` | Adiciona leads de um CSV. Deduplica por @, respeita a lista de não contato |
| `pnpm leads:export` | Exporta todos os leads para `exports/leads-AAAAMMDD-HHMM.csv` |
| `pnpm stats` | Contagens e previsão em JSON |
| `python3 -m outbound dnc <@> [motivo]` | Coloca um perfil na lista de não contato |

Formato do CSV de importação: `kind,segment,name,handle,source_kind,source_ref,source_url,signal,signal_date,score,status`.
`kind` é `client`, `partner` ou `intel`.

## Painel

Atualiza sozinho a cada 5 segundos: totais por tipo e status, enviados hoje contra o limite, previsão de término da fila, plano dos próximos dias, segmentos, lista de leads com filtros, últimos disparos e eventos. O botão **Pausar / retomar** liga e desliga o envio. O envio começa **pausado**.

## Regras de envio (padrão)

- Aquecimento: 5 mensagens por dia na primeira semana, +5 por semana, teto de 30.
- Horário comercial (9h às 20h, Brasília), dias úteis, com 90 a 240 segundos aleatórios entre envios.
- Pausa total ao primeiro alerta, bloqueio ou erro da plataforma.
- Só envia com autorização do operador. A lista de não contato é permanente.
- Navegador sempre **com janela visível**. O operador faz o login; este projeto nunca digita senha nem código.
- Não simula comportamento humano para disfarçar automação, e não contorna CAPTCHA nem bloqueios.
- A sessão do navegador é escolhida pela variável `IG_SESSION` (padrão `ig-session`).

## Estrutura

```
outbound/        pacote Python: db, forecast, dashboard (painel), cli
sender/          protótipo supervisionado de envio (agent-browser, com janela)
tests/           testes (unittest)
docs/PLAN.md     plano, decisões e riscos
data/ exports/ imports/   dados locais, fora do git
```

## Aviso

Envio automatizado de mensagens pode violar os termos de uso da plataforma e restringir a conta. Mantenha volume baixo, aumente aos poucos e use uma conta própria para essa operação. Prospecção B2B deve respeitar a LGPD: abordar empresas com base em informação pública e profissional, e atender de imediato qualquer pedido para parar.
