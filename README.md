# 🌍 T.E.R.R.A.

### Tutor Ecológico de Rotinas e Reduções Ambientais

Aplicativo web que analisa a rotina de uma pessoa, calcula **quanta água ela
gasta de verdade** e transforma as mudanças possíveis em **missões** que dão XP
e fazem o usuário evoluir de *Semente* até *Floresta*.

> Projeto final do curso **Python Pro — Kodland**
> Autor: **Teodoro Paro Vinhal**

---

## 📌 O problema

De toda a água do planeta, menos de **1%** está disponível em rios e lagos. Mesmo
assim, uma pessoa no Brasil costuma gastar bem mais do que os **110 litros por
dia** que a ONU indica como suficiente para viver bem.

O problema quase nunca está em uma única atitude gigante. Ele está nos cinco
minutos extras de banho, na torneira aberta durante a escovação, na pilha jogada
no lixo comum. São gestos pequenos repetidos todos os dias — e é exatamente por
isso que eles somam tanto.

Campanhas ambientais costumam falar em toneladas e em anos, números que ninguém
sente no dia a dia. O T.E.R.R.A. faz o contrário: pega a rotina de **uma pessoa
só**, mostra o impacto dela **em litros** e transforma a mudança em missões
pequenas, com progresso visível. Habito novo se constrói por repetição, não por
culpa.

---

## ✨ O que o app faz

| Funcionalidade | Como funciona |
|---|---|
| **Analisa a rotina** | Formulário com banho, descarga, torneira, lixo e horários |
| **Calcula o consumo** | Litros por dia, mês e ano, separados por atividade |
| **Compara com a ONU** | Mostra quanto você está acima ou abaixo dos 110 L/dia |
| **Escolhe missões** | Regras `if/else` comparam sua rotina com 22 missões do catálogo |
| **Missão do dia** | Sorteada com `random`, estável durante o dia inteiro |
| **Lembretes por horário** | De manhã fala do banho, de noite fala do lixo (`datetime`) |
| **Clima real** | API Open-Meteo; se vai chover, libera a missão de reaproveitar água |
| **Sistema de evolução** | Missão concluída dá XP → Semente, Broto, Muda, Árvore, Floresta |
| **Notificação no PC** | `plyer` manda o lembrete para a área de trabalho |
| **IA opcional** | A API do Claude reordena e explica as missões escolhidas |

---

## 🚀 Como rodar

Precisa de **Python 3.12** (ou 3.11) instalado.
Para ver quais versões você tem: `py -0`

```bash
git clone https://github.com/teoz11n/Projeto-Final-Kodland-Pythonpro.git
```
```bash
cd Projeto-Final-Kodland-Pythonpro
```
```bash
py -3.12 -m venv .venv
```
```bash
.venv\Scripts\activate
```
```bash
pip install -r requirements.txt
```
```bash
python app.py
```

Depois abra **http://127.0.0.1:5000** no navegador.

O banco de dados `terra.db` é criado **sozinho** na primeira execução — não
precisa rodar nenhum script antes.

Para parar o servidor: `Ctrl+C`. Para sair do ambiente virtual: `deactivate`.

<details>
<summary>No Linux ou no Mac os comandos mudam um pouco</summary>

```bash
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python app.py
```
</details>

---

## 🤖 Ativar a IA (totalmente opcional)

**O app funciona 100% sem isso.** Sem chave, ele escolhe as missões pelas
regras do `missoes.py`.

Se quiser ativar, copie o modelo e cole sua chave:

```bash
copy .env.example .env
```

Abra o `.env` e troque o texto de exemplo pela sua chave do
[console.anthropic.com](https://console.anthropic.com).

Com a IA ligada, cada missão ganha uma linha **"Por que para você:"** explicando
a escolha com base nos seus números.

> ⚠️ O arquivo `.env` está no `.gitignore` e **nunca** sobe para o GitHub.
> Só o `.env.example` (sem chave nenhuma) fica no repositório.

---

## 📂 Estrutura do projeto

```
.
├── app.py              # rotas do Flask — só chama as outras funções
├── calculos.py         # constantes de referência + contas de água e níveis
├── missoes.py          # regras if/else que escolhem as missões
├── missoes.json        # catálogo com 22 missões e 8 dicas
├── clima.py            # integração com a API Open-Meteo
├── ia.py               # integração opcional com a API do Claude
├── notificacoes.py     # notificação no computador com plyer
├── database.py         # cria as tabelas, salva e lê os dados
├── requirements.txt    # bibliotecas que precisam ser instaladas
├── .env.example        # modelo para a chave da API (sem a chave real)
├── templates/
│   ├── base.html       # molde com o menu, usado por todas as outras
│   ├── _graficos.html  # plantas em SVG + a macro planta() que as posiciona
│   ├── _personagens.html # a macro agente(), que desenha a ficha de fala
│   ├── index.html      # apresentação, com o hero e a colagem final
│   ├── rotina.html     # formulário
│   ├── resultado.html  # consumo, comparação com a ONU e missões
│   ├── painel.html     # missão do dia, lembrete, clima
│   ├── perfil.html     # nível, XP, histórico
│   ├── sobre.html      # problema, fontes e autor
│   └── 404.html        # página de erro
├── static/
│   ├── style.css       # o sistema de design inteiro, em 21 blocos
│   ├── efeitos.js      # efeitos de interface, JavaScript puro
│   └── personagens/    # as 5 ilustrações da equipe da Estação
├── docs/PROPOSTA.md    # o planejamento original entregue no curso
└── extras/             # exercícios anteriores, fora do escopo do T.E.R.R.A.
```

### As páginas

| Endereço | O que mostra |
|---|---|
| `/` | Apresentação e botão para começar |
| `/rotina` | Formulário da rotina (cadastro e edição) |
| `/resultado` | Consumo calculado, comparação com a ONU e missões sugeridas |
| `/painel` | Missão do dia, lembrete, clima e missões ativas |
| `/perfil` | Nível, XP, barra de progresso, histórico e total economizado |
| `/sobre` | O problema climático, as fontes dos dados e o autor |

---

## 🧠 Como o código está organizado

A regra principal é **separar a lógica das rotas**:

- O `app.py` é um **garçom**: recebe o pedido do navegador, chama as funções dos
  outros arquivos e entrega o resultado para o template. Nenhuma conta de litros
  acontece lá dentro.
- O `calculos.py` **não sabe** o que é Flask, nem HTML, nem banco de dados. Ele
  só recebe números e devolve números — por isso é fácil de testar.

Três decisões que valem destaque:

**1. O XP não é um campo solto.** Ele é a `SUM()` da tabela `missoes_concluidas`.
Assim é impossível o XP ficar diferente do histórico que aparece na tela.

**2. A IA nunca inventa missão.** Ela só reordena e explica missões que as regras
já aprovaram. Se a chave não existir ou a API falhar, tudo cai no `except` e o
app volta para as regras sozinho. O mesmo vale para o clima: se a Open-Meteo não
responder, o bloco do clima simplesmente desaparece da tela.

**3. A economia não é uma soma simples.** Três missões diferentes mexem no mesmo
chuveiro — somar as três daria um número maior do que a pessoa gasta de verdade.
Por isso cada missão tem um `grupo` no `missoes.json`, e a função
`economia_combinada()` conta só a melhor de cada grupo.

---

## 📊 Fontes dos dados

Todos os valores de referência estão como **constantes no topo do
`calculos.py`**, cada um com a fonte no comentário. Se um órgão atualizar um
número, basta trocar em um lugar só.

| Dado | Valor usado | Fonte |
|---|---|---|
| Vazão do chuveiro elétrico | 9 L/min | SABESP / ANA |
| Descarga de caixa acoplada | 10 L por acionamento | ANA — Manual de Conservação de Água |
| Torneira de pia aberta | 6 L/min | SABESP — tabela de consumo doméstico |
| Consumo recomendado | 110 L por pessoa/dia | ONU / PNUMA |
| Clima e previsão de chuva | tempo real | [Open-Meteo](https://open-meteo.com) |

---

## 🛠️ Tecnologias

- **Python 3.12** + **Flask** — interface web
- **SQLite** (`sqlite3`) — perfis, progresso e missões concluídas
- **Jinja2** — templates HTML
- **requests** — conversa com as APIs
- **datetime** — rotina, horários e lembretes
- **random** — sorteio da missão do dia e das dicas
- **json** — catálogo de missões e dicas
- **plyer** — notificação no computador *(opcional)*
- **API Open-Meteo** — clima, gratuita e sem chave
- **API do Claude** — interpretação da rotina *(opcional)*

> O leitor do arquivo `.env` foi escrito à mão dentro do `ia.py` (10 linhas) para
> não precisar instalar o `python-dotenv`. Uma dependência a menos.

---

## 🌱 Níveis

| Nível | Nome | XP necessário |
|:---:|---|---:|
| 1 | Semente | 0 |
| 2 | Broto | 50 |
| 3 | Muda | 120 |
| 4 | Árvore | 250 |
| 5 | Floresta | 500 |

Cada missão vale de **10 a 40 XP**, de acordo com a dificuldade. A mesma missão
só pode ser concluída **uma vez por dia** — o app verifica a data antes de dar
o XP.

---

## 🚀 Funcionalidades futuras

- Ranking e desafios entre amigos e familiares
- Conquistas e medalhas para sequências de missões
- Cálculo da pegada de carbono, com gráficos semanais e mensais
- Mapa de pontos de coleta seletiva perto do usuário
- Integração com WhatsApp ou Telegram
- Versão para celular
- Missões em grupo para escolas, com metas coletivas

---

## 🎨 Identidade visual

### Paleta

A [paleta oficial](https://coolors.co/ffdd00-8eee43-1cff86-ffffff-59d2fe-4a8fe7-384296)
está como variáveis CSS no topo do `static/style.css`:

| | Cor | Uso |
|:--:|---|---|
| 🟡 | `#FFDD00` amarelo | missões de descarte, girassol |
| 🟢 | `#8EEE43` verde-folha | folhagem, degradês |
| 💚 | `#1CFF86` verde-neon | destaque, XP, a palavra viva |
| ⚪ | `#FFFFFF` branco | superfícies e vidro |
| 🔵 | `#59D2FE` azul-céu | água, clima |
| 🔷 | `#4A8FE7` azul | botões |
| 🔹 | `#384296` azul-noite | **a tinta de todo o texto** |

> ⚠️ O verde-neon tem contraste de **1,4:1** no branco. É ilegível em texto
> corrido, então ele só aparece em título gigante e em preenchimento. O texto
> usa sempre o azul-noite, que dá 10:1.

### Tipografia

| Papel | Fonte | Fallback livre |
|---|---|---|
| Display | **TAN Meringue** (paga) | Playfair Display |
| Script | **Sloop Script** (paga) | Pinyon Script |
| Texto | **Noto Serif Bengali** | — (é livre) |

Como ativar as fontes pagas está explicado no bloco **02 FONTES** do
`static/style.css` — junto do código que usa elas.

### A progressão de vida

A ideia central do visual: no **topo da página** os elementos de natureza
ficam lavados, quase brancos, para o texto ter contraste. Conforme a pessoa
desce, eles vão ganhando cor, até a **colagem final**, onde a paleta é
liberada (entram rosa, roxo e laranja) e as folhas ficam 100% vivas e
sobrepostas.

Isso é uma variável CSS só. Cada seção declara quanta vida ela tem:

```css
.vida-1 { --vida: .18; }   /* hero: quase branco  */
.vida-5 { --vida: 1; }     /* colagem: tudo vivo  */

.planta {
  opacity: calc(.25 + var(--vida) * .75);
  filter: saturate(calc(.12 + var(--vida) * .88));
}
```

### Os desenhos

Todas as plantas são **SVG desenhado à mão** em `templates/_graficos.html` —
monstera, samambaia, palmeira, arbusto florido, girassol, flor, ramo e gota.
Nenhuma imagem é baixada, nada fica borrado em tela grande, e dá para
recolorir qualquer uma pelo CSS:

```html
<svg class="planta" style="--c1:#FF9FC4"><use href="#palma"/></svg>
```

As manchas de aquarela usam um filtro SVG (`feTurbulence` +
`feDisplacementMap`) que embaralha as bordas, para elas não ficarem com
cara de círculo de computador.

---

## ✨ Efeitos de interface

Tudo em **CSS e JavaScript puros**. Nenhuma biblioteca, nenhum CDN, nenhum
build step — o que também significa que dá para explicar cada linha.

| Efeito | Onde está |
|---|---|
| **Liquid glass** | `.vidro` — blur + `saturate(185%)` + reflexo na borda de cima |
| **Cursor tracking glow** | brilho que segue o mouse dentro dos cartões |
| **Hover lift** | o botão sobe e a sombra cresce junto |
| **Magnetic hover** | `.magnetico` — o botão é atraído pelo cursor |
| **Spring animation** | curva `--mola` com overshoot, dá peso físico |
| **Icon slide** | a setinha `→` desliza no hover |
| **Shimmer** | reflexo que atravessa o botão |
| **Border beam** | feixe girando na borda (`@property --angulo`) |
| **Scroll reveal** | entrada em sequência via `IntersectionObserver` |
| **Parallax** | as plantas andam mais devagar que a página |
| **Number counter** | os litros sobem de 0 até o valor |
| **Scroll progress** | barra fininha no topo |
| **Back to top** | botão flutuante depois de meia tela |
| **Toasts** | os avisos do Flask somem sozinhos |
| **Floating label** | o rótulo do campo sobe quando você digita |
| **Film grain** | ruído de 3,5% por cima de tudo |

### Três decisões que valem explicar

**1. O conteúdo do topo não depende de JavaScript.** O resto da página usa
`.revelar` (que precisa do JS para aparecer), mas o hero usa `.entrada`, que é
animação de CSS puro. Se o JS falhar, a primeira coisa que a pessoa vê não
pode ser uma tela em branco.

**2. O contador nunca mostra número errado.** O valor verdadeiro já vem no
HTML. O JavaScript só zera e anima os números que estão visíveis na tela
naquele momento. Se a animação não rodar, a pessoa vê `520.0` — nunca `0,0`.

**3. `prefers-reduced-motion` é respeitado.** Quem pediu menos animação no
sistema recebe a página sem movimento nenhum. Não é enfeite: excesso de
animação causa enjoo em algumas pessoas.

---

## 📄 Documentos

- [**Proposta original do projeto**](docs/PROPOSTA.md) — o planejamento entregue
  no curso, com o problema, os objetivos e o público-alvo.

---

## 👤 Autor

**Teodoro Paro Vinhal**
Projeto final do curso Python Pro — [Kodland](https://kodland.org/br/)
