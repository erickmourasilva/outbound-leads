# AGENTS.md

Outbound e extração de leads. Para agentes de IA (Claude Code, Codex etc.): leia `skills/outbound-leads/SKILL.md`, que traz o fluxo completo, os comandos e as regras.

Início rápido:

```bash
python3 -m outbound setup        # instala o que falta e cria o banco (~/.outbound-leads); --check só verifica
./setup.sh                       # o mesmo, macOS/Linux (Windows: .\setup.ps1)
python3 -m outbound doctor       # diagnóstico em JSON
python3 -m outbound serve        # painel ao vivo em 127.0.0.1
python3 -m unittest discover -s tests
```

Respostas: o outbound só abre a conversa; antes do primeiro envio rode `python3 -m outbound replies`, apresente a recomendação (com a divulgação) uma vez e registre a escolha.

Regras: nada é enviado sem autorização do operador; navegador sempre com janela visível; o login é do operador; nunca disfarçar automação nem contornar bloqueios; dados de leads ficam em `~/.outbound-leads`, nunca no código.
