# Segurança e uso responsável

> 🇬🇧 [English version](SECURITY.en.md)

## Reportando uma vulnerabilidade

Reporte problemas de segurança em privado pelo GitHub: **Security → Report a vulnerability** neste repositório. Não abra issue pública para vulnerabilidades.

## Notas de projeto

- O painel escuta só em `127.0.0.1` e aceita alterações apenas com um cabeçalho personalizado, o que bloqueia requisições de outros sites.
- Os dados ficam num arquivo SQLite local (`~/.outbound-leads`). Este projeto não envia nada para nenhum servidor.
- A ferramenta nunca digita senhas, códigos ou tokens. O login é feito pelo operador numa janela de navegador visível.

## Uso responsável

Mensagens automatizadas podem violar os termos da plataforma e a lei local (como a LGPD e regras contra spam). Use uma conta dedicada, mantenha o volume baixo, atenda todo pedido para parar e use só informação pública e profissional. A responsabilidade pelo uso do software é de quem o usa.
