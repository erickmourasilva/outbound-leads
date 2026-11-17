# Extrair leads dos seguidores de perfis de concorrentes (Instagram)

Seguidores de um concorrente costumam ser agências, clientes e parceiros do mesmo mercado. É uma fonte útil, mas **o Instagram limita e vigia a leitura de listas de seguidores**. Faça devagar, em janela visível, e pare ao primeiro aviso.

## Pré-requisitos

- O operador está logado na janela visível (`agent-browser --headed`). Você nunca digita credenciais.
- Preferir uma **conta separada** da conta principal de atendimento, porque uma restrição atinge a conta inteira.

## Procedimento

1. Abra o perfil do concorrente e clique em **Seguidores**.
2. Role a lista em passos curtos, com pausa entre os passos, e leia o texto de cada bloco (`snapshot`, `get text`). Não passe de cerca de **50 perfis por sessão** e de uma sessão por dia por concorrente.
3. Descarte na hora: perfis pessoais, menores de idade, perfis privados, contas sem bio ou sem sinal de negócio.
4. Para cada candidato que pareça comercial (categoria, serviço, cidade, site na bio), abra o perfil e leia só o que é público: nome, bio, categoria, cidade, link do site. Confirme que é uma empresa e a qual segmento pertence.
5. Registre uma linha no CSV de importação:
   - `source_kind=competitor_followers`, `source_ref=@concorrente`
   - `kind`: `partner` se presta serviço de CRM, marketing ou automação; `client` se é o público final; `intel` se é outro concorrente
   - `signal`: o que há de **útil no próprio perfil** (ex.: "clínica odontológica em Curitiba, 3 unidades"). O fato de seguir o concorrente é só a origem; não o use como sinal.
6. Rode `python3 -m outbound import arquivo.csv` e qualifique com `leads set-status <@> qualified`.

## Parar imediatamente

Aviso de atividade incomum, tela de "tente novamente mais tarde", pedido de verificação, queda de login ou listas que deixam de carregar. Feche a sessão, **não retome no mesmo dia** e avise o usuário. Nunca tente contornar.

## Não faça

- Guardar a lista bruta de seguidores. Guarde só os candidatos qualificados.
- Coletar telefone, e-mail pessoal, dados de contas pessoais ou qualquer traço sensível.
- Dizer na mensagem que a pessoa segue o concorrente.
