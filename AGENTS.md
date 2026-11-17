# AGENTS.md

Projeto pessoal de outbound e extração de leads. Para agentes de IA (Claude Code, Codex etc.): leia `skills/outbound-leads/SKILL.md`, que traz o fluxo completo, os comandos e as regras.

Início rápido:

```bash
./setup.sh                       # verifica o ambiente e cria o banco local (~/.outbound-leads)
python3 -m outbound doctor       # diagnóstico em JSON
python3 -m outbound serve        # painel ao vivo em 127.0.0.1
python3 -m unittest discover -s tests
```

Regras: nada é enviado sem autorização do operador; navegador sempre com janela visível; o login é do operador; nunca disfarçar automação nem contornar bloqueios; dados de leads ficam em `~/.outbound-leads`, nunca no código.
