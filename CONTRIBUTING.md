# Contribuindo

Obrigado por ajudar. Este projeto existe para tornar o outbound **gradual, supervisionado e honesto**, então as contribuições são avaliadas por esses princípios (veja o README).

> 🇬🇧 [English version](CONTRIBUTING.en.md)

## Preparação

```bash
git clone https://github.com/erickmourasilva/outbound-leads && cd outbound-leads
python3 -m outbound setup --check
python3 -m unittest discover -s tests -v
```

Python 3.10+ e só a biblioteca padrão. Não adicione dependências de execução sem discutir antes.

## Pull requests

- Uma mudança focada por PR, com testes. A CI roda em macOS, Linux e Windows.
- Nada de dados de usuário no repositório: sem leads, perfis, mensagens ou capturas de tela reais. Use o comando `demo` para exemplos.
- Os comandos devem continuar imprimindo JSON, para que agentes consigam ler.

## O que não será aceito

- Qualquer coisa que disfarce a automação (digitação simulada, falsificação de fingerprint) ou contorne CAPTCHA, limites de taxa ou bloqueios.
- Recursos que coletem telefone ou e-mail pessoal, atributos sensíveis, ou que extraiam dados privados ou protegidos.
- Padrões que enviem sem aprovação explícita do operador ou que aumentem os tetos de envio.

## Reportando bugs

Abra uma issue com a saída de `python3 -m outbound doctor` e o seu sistema operacional. Para falhas de segurança, veja o `SECURITY.md`.

## Versões

O Claude Code só oferece atualização do plugin quando o número da versão muda. **Toda mudança em `skills/`, `outbound/` ou nos manifestos precisa subir `version` em `.claude-plugin/plugin.json` e registrar no `CHANGELOG.md`.**
