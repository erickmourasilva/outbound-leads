# Envio supervisionado

Um lead por vez. O usuário acompanha pela janela visível e pelo painel.

## Antes de cada envio

```bash
python3 -m outbound next
```

Só prossiga se `allowed` for `true`. Se não for, leia `reason`: `paused`, `weekend`, `outside_hours`, `daily_cap_reached` ou `min_interval` (aguarde `wait_seconds`). O envio começa pausado: `resume` só com o usuário pedindo.

## Passo a passo (Instagram, `agent-browser`)

1. `agent-browser --headed --session ig-session --session-name ig-session open https://www.instagram.com/<handle>/`. Se pedir login, **o usuário entra na janela**; nunca digite credenciais.
2. `wait 4500` e `snapshot -i`. **Confirme a identidade**: o nome, a bio e a cidade conferem com o lead (faça uma captura de tela se houver dúvida). Se não conferir, não envie.
3. Seguir antes só se o usuário tiver pedido. Se pedido, `click` em "Seguir" e confirme "Seguindo".
4. `click` em "Enviar mensagem". Se aparecer uma caixa com "mensagem prioritária" e "solicitação de contato", escolha a **solicitação de contato** (a prioritária pode ter custo ou rótulo especial).
5. Clique no campo "Mensagem...". Digite cada parágrafo com `keyboard inserttext`, e entre os parágrafos use `press Shift+Enter` duas vezes (só Enter envia).
6. Faça uma captura de tela e confira: destinatário certo, texto íntegro, parágrafos separados.
7. `press Enter`. Confira que o balão apareceu.
8. Se surgir o aviso "não aceita novas solicitações de contato", registre `not_accepting`.
9. Registre: `python3 -m outbound record-send <handle> ok --message-file <arquivo>` (ou `--message`).
10. Aguarde `suggested_delay_after_send` segundos antes do próximo (o `next` recalcula).

## Parar imediatamente

Qualquer aviso da plataforma, "tente novamente mais tarde", ação bloqueada, pedido de verificação, queda de login ou comportamento inesperado: `record-send <handle> blocked` (pausa tudo), feche a sessão e avise o usuário. Não tente contornar nem repetir.

## Depois do lote

Se o usuário tiver pedido para seguir antes, deixe de seguir ao concluir: abra o perfil, "Seguindo" → "Deixar de seguir", e confirme que voltou a "Seguir". Feche a sessão do navegador. As respostas chegam ao CRM do usuário, não aqui.
