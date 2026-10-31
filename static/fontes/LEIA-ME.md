# Pasta das fontes

As duas fontes principais do projeto são **comerciais** e não estão no Google
Fonts, então não podem ser distribuídas junto com o código.

| Fonte | Onde é usada | Situação |
|---|---|---|
| **TAN Meringue** | títulos gigantes (`--fonte-display`) | paga, [TAN Type Foundry](https://www.creativemarket.com/tanstudio) |
| **Sloop Script** | a assinatura manuscrita (`--fonte-script`) | paga, Sudtipos / Font Bureau |
| **Noto Serif Bengali** | texto de leitura (`--fonte-texto`) | livre, já carregada do Google Fonts |

## Enquanto você não tem as fontes pagas

O site **já funciona normalmente**. O `style.css` usa uma cascata de três
níveis e cai sozinho nos substitutos livres:

- TAN Meringue → **Playfair Display** (serifada de alto contraste, mesma pegada)
- Sloop Script → **Pinyon Script** (caligráfica)

## Quando você tiver as fontes

Tem dois caminhos. O primeiro é mais fácil:

**1. Instalar no Windows** — clique duplo no arquivo da fonte e em "Instalar".
Pronto, o site passa a usar ela automaticamente (é o que o `local()` faz no
`@font-face`). Mas só funciona no seu computador.

**2. Colocar o arquivo aqui** — serve para qualquer pessoa que abrir o site.

1. Converta a fonte para `.woff2` (use o [Font Squirrel Webfont Generator](https://www.fontsquirrel.com/tools/webfont-generator))
2. Salve nesta pasta com exatamente estes nomes:
   - `TANMeringue.woff2`
   - `SloopScriptOne.woff2`
3. Abra o `static/style.css`, ache o bloco **02 FONTES** e tire os `/*` e `*/`
   das duas linhas `url(...)` que estão comentadas.

> **Atenção com a licença:** colocar o arquivo da fonte numa pasta pública do
> GitHub é **distribuir** a fonte. A licença de uma fonte comercial quase
> sempre proíbe isso. Para um projeto escolar, o caminho 1 (instalar no seu
> PC) é o mais seguro.
