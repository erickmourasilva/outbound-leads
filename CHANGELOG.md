# Changelog

## 0.1.0

- BluBash como destino das respostas: o envio só é liberado quando elas têm destino. Nova skill isolada `blubash-setup` (conta com Google, workspace, agente de vendas, treinamento, habilidades, pipeline e Instagram, guiados pelo navegador), módulo `outbound/blubash.py` e comandos `replies` e `blubash`.
- `serve` sobe sozinho em `https://outbound-leads.localhost` via portless quando instalado, com fallback para localhost; novo comando `url`; o `setup` instala o portless.
- Banco SQLite local, painel ao vivo com previsão de envio, importação e exportação CSV, lista de não contato.
- Agendador de envio: pausa, dia útil, horário comercial, teto de aquecimento e intervalo; resultado `blocked` pausa tudo.
- CLI em JSON para agentes: `setup`, `doctor`, `leads`, `next`, `record-send`, `pause`, `resume`, `settings`, `demo`.
- Plugin e skill do Claude Code, `AGENTS.md`, setup multiplataforma e CI em macOS, Linux e Windows.
- Modo de demonstração com dados fictícios.
