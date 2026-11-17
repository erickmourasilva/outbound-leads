# Solução de problemas

Consulte a documentação antes de improvisar: https://docs.blubash.io/pt-BR

| Situação | O que fazer |
|---|---|
| A janela do Instagram não abre | O navegador bloqueou o pop-up. Libere pop-ups para `app.blubash.io` e clique em **Conectar com Instagram** de novo. |
| "Popup de configuração foi fechado" | A janela foi fechada antes de terminar. Clique em **Tentar novamente** e peça ao usuário para concluir o login e a autorização. |
| "Falha ao conectar Instagram" | Confirme que a conta é **profissional** (comercial ou criador) e repita. |
| A tela avisa que a conta já está em uso | Use o canal que já existe para essa conta, ou desconecte-o antes de criar outro. |
| Conectou, mas as mensagens não chegam | No app do Instagram, em configurações de mensagens, confirme que o acesso às mensagens por ferramentas conectadas está permitido. Mande uma DM de outra conta para testar. |
| A conversa nova não mostra a DM que o outbound enviou | Confira no teste de ponta a ponta. Se a mensagem original não aparecer, o agente não a viu, e por isso o Comportamento nunca depende dela. |
| Só dá para responder por 7 dias | É a janela do Instagram: a equipe responde até 7 dias após a última mensagem do contato. O agente cuida das respostas na hora. |
| Agente não responde | Veja se está **Ativo**, vinculado ao canal Instagram (Configurações do Canal), com treinamento **Treinado** e se o plano tem créditos de IA. |
| Diálogo de limite de agentes, canais, pipelines ou créditos que bloqueia a etapa | Pare e explique as opções (desativar outro agente, ajustar o plano). A decisão e o pagamento são do usuário. |
| Faixa de teste de 7 dias | **É esperada. Não pare.** Ignore ou feche e siga o escopo. |
| Página de pagamento, ou pedido de cartão, CPF/CNPJ ou endereço fiscal | Pare. O usuário decide e paga. Você nunca preenche esses dados. |
| "Testar Agente" com o campo desabilitado ou com erros repetidos | Feche o painel, pare e chame o usuário. Não pule a etapa sozinho: o usuário decide se segue sem o teste e volta a ele depois. |
| Um clique não faz nada e não dá erro | O botão estava fora da tela: use `scrollintoview @ref` antes do `click` e confirme que a tela mudou. |
| Dois workspaces com nome parecido | O workspace atual aparece destacado no seletor de workspaces (menu do avatar). Confirme qual é antes de criar qualquer coisa. |
| Transferência não acontece | A equipe de destino precisa ter acesso ao canal do Instagram. |
| Treinamento "Falhou" | Remova o item e adicione de novo. Se persistir, simplifique o conteúdo e tente outra vez. |
| Login do Google pede verificação extra | É com o usuário. Aguarde, sem tentar contornar. |
| Os nomes na tela não batem com o runbook | Use o `snapshot` e a documentação pública. A interface pode mudar. |

## Regras

- Nunca peça nem digite senha, código de verificação ou dado de pagamento.
- Nunca marque uma etapa como feita sem ver o resultado na tela.
- Se travar duas vezes na mesma tela, descreva o problema ao usuário e peça orientação.
