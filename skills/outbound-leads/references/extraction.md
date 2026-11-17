# Extração e segmentação

## Fontes permitidas

- **Diretórios públicos de parceiros de concorrentes** ("encontre um parceiro", agências parceiras). Melhor ponto de partida: sem login.
- Páginas de cases e depoimentos, notícias de expansão, vagas de atendimento/SDR, avaliações públicas.
- **Listas de seguidores de perfis de concorrentes**, só com a conta do operador já logada na janela visível: ritmo lento, poucas dezenas por sessão, apenas contas **comerciais** (bio com serviço, categoria, cidade, site). Parar ao primeiro aviso da plataforma. Prefira uma conta separada da conta principal.

Fora do limite: login de terceiros, grupos privados, bases vazadas, corretores de dados, telefone ou e-mail pessoal, perfis de pessoas físicas, qualquer traço sensível.

## O @ do Instagram

Sempre vem de uma fonte verificável: o link no site oficial da empresa ou o próprio perfil aberto. Nunca adivinhe um @. Sem @ verificado, não entra.

## Ferramentas

- WebFetch/WebSearch para páginas simples.
- `agent-browser --headed --session <nome> open <url>`, `wait 4000`, `snapshot`, `get text body`, `click @ref`, `scroll down`, `close` para páginas dinâmicas. Use uma sessão por tarefa.
- Para volume, rode subagentes em paralelo, um por fonte, cada um gravando um CSV em `~/.outbound-leads/imports/`. Diga a cada um: só URLs que abriu e leu; parar em CAPTCHA/login; sem contato pessoal.

## CSV de importação

Cabeçalho exato:

```
kind,segment,name,handle,source_kind,source_ref,source_url,signal,signal_date,score,status
```

- `kind`: `client` (quem pode comprar), `partner` (agência, consultoria, integrador, revenda), `intel` (concorrente a sondar).
- `handle`: sem arroba, minúsculo.
- `source_kind`: `competitor_directory`, `competitor_followers`, `news`, `job`, `maps`, `manual`.
- `source_ref`: de qual concorrente ou diretório veio.
- `signal`: frase curta sobre o que a fonte diz. `signal_date`: vazio se não houver.
- `score` 0 a 100; `status` normalmente `discovered`.

`python3 -m outbound import arquivo.csv` deduplica por @ e ignora quem está em não contato. Depois, qualifique: `leads set-status <@> qualified`.

## Pontuação (sugestão)

Dor ou gatilho recente (30), encaixe com o segmento alvo (30), sinal datado nos últimos 6 meses (20), canal público verificado (10), porte plausível (10). Descarte quem não tem sinal.
