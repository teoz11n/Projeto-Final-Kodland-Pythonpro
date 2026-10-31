# Extras

Exercícios e testes de outras aulas do curso, guardados aqui para não se
perderem. **Não fazem parte do T.E.R.R.A.** e não são necessários para rodar
o aplicativo.

| Arquivo | O que é |
|---|---|
| `bot_discord.py` | Bot de Discord que responde `!start` e `!fact`: busca uma curiosidade aleatória numa API, traduz para o português e fala em voz alta. Usa `discord.py`, `pyttsx3` e `deep-translator` — bibliotecas que **não** estão no `requirements.txt` do projeto principal. |

> ⚠️ O `bot_discord.py` tem `bot.run("seu token")` no final. Se um dia for usar
> de verdade, nunca cole o token direto no código: guarde em um arquivo `.env`,
> como o T.E.R.R.A. faz com a chave da API.
