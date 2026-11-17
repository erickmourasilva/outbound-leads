---
name: outbound-leads
description: >-
  Outbound e extração de leads. Use quando o usuário pedir para extrair leads,
  montar lista de prospecção, achar parceiros ou clientes a partir de
  concorrentes (diretórios de parceiros, cases, listas de seguidores),
  segmentar e pontuar leads, disparar mensagens diretas aos poucos (aquecimento
  gradual), acompanhar envios num painel ou ver a previsão da fila. Também para
  "instalar o outbound-leads", "outbound", "prospecção ativa", "disparar DMs",
  "painel de leads". Mensagens só saem com autorização do operador, com janela
  de navegador visível e limites diários baixos.
---

# outbound-leads

Motor local de outbound: **extrair → segmentar → enviar aos poucos → acompanhar**. As respostas e a conversa de venda ficam no CRM do usuário; aqui só existe a parte ativa.

Os dados ficam em `~/.outbound-leads` (variável `OUTBOUND_HOME`), fora do código. Todo comando abaixo imprime JSON.

## 1. Preparar (faça sozinho)

O motor está em `<diretório desta skill>/../..`. Entre nele e rode:

```bash
cd "<raiz do motor>" && python3 -m outbound doctor
```

`doctor` diz o que falta e como corrigir. Só Python 3.11+ é obrigatório (biblioteca padrão). Para **enviar**, o `agent-browser` também é necessário (`npm install -g agent-browser`). `pnpm install` é opcional: dá a URL nomeada do painel via `pnpm dev`.

Painel ao vivo: `python3 -m outbound serve` (ou `pnpm dev`), em segundo plano. Abra-o numa janela **visível** para o usuário acompanhar.

## 2. Fluxo

| Etapa | O que fazer | Referência |
|---|---|---|
| Extrair | Reunir leads de fontes públicas e gravar em CSV; `import` deduplica e respeita a lista de não contato | `references/extraction.md` |
| Segmentar | Definir `kind` (client, partner, intel), segmento, sinal público e pontuação | `references/extraction.md` |
| Mensagens | Redigir modelos curtos, fundamentados no sinal público; **o usuário aprova** | `references/messages.md` |
| Fila | `leads set-status <@> approved` nos aprovados | – |
| Enviar | Um por vez, supervisionado, respeitando `next` | `references/sending.md` |
| Acompanhar | Painel, `stats` e previsão | – |

## 3. Comandos

| Comando | Para quê |
|---|---|
| `doctor` | Verifica o ambiente |
| `import arquivo.csv` / `export` | Entrada e saída em CSV |
| `leads list [--status S] [--kind K]` / `leads add ...` / `leads set-status <@> <status>` | Gerenciar leads |
| `next [--limit N]` | **Posso enviar agora?** Retorna `allowed`, motivo, limite do dia, espera e os próximos leads |
| `record-send <@> ok\|failed\|not_accepting\|blocked [--message ...]` | Registra cada envio. `blocked` pausa tudo |
| `pause` / `resume` | Chave geral. O envio **começa pausado** |
| `settings [chave valor]` | Limites: `base_daily`, `weekly_step`, `max_daily`, horários, intervalos |
| `dnc <@> [motivo]` | Não contatar, para sempre |
| `stats` | Contagens e previsão |
| `serve [--port N]` | Painel local |

Status dos leads: `discovered → qualified → approved → queued → sent` (saídas: `skipped`, `failed`, `do_not_contact`).

## 4. Regras que não mudam

1. **Nunca envie sem autorização do usuário** para os textos e a lista. Autorização permanente só se ele disser isso com clareza; mesmo assim, só dentro dos limites do `next`.
2. **Janela do navegador sempre visível** (`agent-browser --headed`). O usuário faz o login. Nunca digite senha, código ou token.
3. **Não disfarce a automação.** Não simule digitação humana para enganar detecção, não contorne CAPTCHA, bloqueio ou limite. Ritmo gradual e conservador é regra de saúde da conta, não disfarce.
4. **Pare ao primeiro alerta, bloqueio ou "tente novamente mais tarde"**: `record-send ... blocked` (pausa tudo) e avise o usuário.
5. **Pedido para parar é atendido na hora** (`dnc`). Nunca reabordar.
6. Só informação pública e profissional de empresas. Sem telefone ou e-mail pessoal, sem traços sensíveis, sem perfis privados.
7. Afirmações nas mensagens só se comprovadas em material público do produto.
8. Avise que envio automatizado pode violar os termos da plataforma e restringir a conta; recomende conta dedicada e volume baixo.
