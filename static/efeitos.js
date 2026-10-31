/* ===================================================================
   efeitos.js - T.E.R.R.A.
   -------------------------------------------------------------------
   Todos os efeitos de interface do site, em JavaScript puro.
   Nenhuma biblioteca, nenhum download, nada de CDN.

   O que tem aqui:
     1. Menu do celular
     2. Navbar que encolhe ao rolar
     3. Barra de progresso de leitura
     4. Botao de voltar ao topo
     5. Revelacao no scroll (com entrada em sequencia)
     6. Botao magnetico
     7. Contador de numeros
     8. Parallax das plantas
     9. Avisos que somem sozinhos

   Regra geral deste arquivo: TUDO e opcional. Se um elemento nao
   existir na pagina, a funcao simplesmente nao faz nada. Assim o
   mesmo arquivo serve para todas as paginas do site.
   =================================================================== */

(function () {
  "use strict";

  // A pessoa pediu menos animacao no sistema operacional?
  // Se sim, desligamos os efeitos de movimento (nao os de utilidade).
  const menosMovimento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Atalhos para nao repetir document.querySelector o tempo todo.
  const pegar = (seletor) => document.querySelector(seletor);
  const pegarTodos = (seletor) => Array.from(document.querySelectorAll(seletor));


  /* =================================================================
     1. MENU DO CELULAR
     ================================================================= */

  function menuCelular() {
    const botao = pegar(".abrir-menu");
    const menu = pegar(".topo nav");
    if (!botao || !menu) return;

    botao.addEventListener("click", function () {
      const aberto = menu.classList.toggle("aberto");
      botao.setAttribute("aria-expanded", aberto ? "true" : "false");
      botao.textContent = aberto ? "✕" : "☰";  // X ou hamburguer
    });
  }


  /* =================================================================
     2 e 3. NAVBAR AO ROLAR + BARRA DE PROGRESSO
     -----------------------------------------------------------------
     Os dois dependem do scroll, entao ficam no MESMO listener.
     Um listener de scroll bem feito nao pode fazer conta pesada:
     por isso usamos requestAnimationFrame, que executa no momento
     certo do desenho do navegador, sem travar a rolagem.
     ================================================================= */

  function aoRolar() {
    const topo = pegar(".topo");
    const progresso = pegar(".progresso-scroll");
    const voltar = pegar(".voltar-topo");
    let agendado = false;

    function atualizar() {
      const y = window.scrollY;

      // Navbar encolhe depois de 30px
      if (topo) topo.classList.toggle("rolou", y > 30);

      // Quanto da pagina ja foi lido, de 0 a 1
      if (progresso) {
        const altura = document.documentElement.scrollHeight - window.innerHeight;
        const lido = altura > 0 ? Math.min(y / altura, 1) : 0;
        progresso.style.setProperty("--lido", lido.toFixed(4));
      }

      // Botao de voltar ao topo aparece depois de meia tela
      if (voltar) voltar.classList.toggle("aparece", y > window.innerHeight * 0.55);

      agendado = false;
    }

    window.addEventListener("scroll", function () {
      if (!agendado) {
        agendado = true;
        window.requestAnimationFrame(atualizar);
      }
    }, { passive: true });

    atualizar();  // roda uma vez ao abrir a pagina
  }


  /* =================================================================
     4. VOLTAR AO TOPO
     ================================================================= */

  function voltarAoTopo() {
    const botao = pegar(".voltar-topo");
    if (!botao) return;

    botao.addEventListener("click", function () {
      window.scrollTo({
        top: 0,
        behavior: menosMovimento ? "auto" : "smooth"
      });
    });
  }


  /* =================================================================
     5. REVELACAO NO SCROLL
     -----------------------------------------------------------------
     IntersectionObserver avisa quando um elemento entra na tela.
     E muito mais leve do que ficar medindo posicao no scroll.
     ================================================================= */

  function revelarNoScroll() {
    const alvos = pegarTodos(".revelar");
    if (!alvos.length) return;

    // Sem suporte ou com movimento reduzido: mostra tudo de uma vez.
    if (menosMovimento || !("IntersectionObserver" in window)) {
      alvos.forEach((el) => el.classList.add("visivel"));
      return;
    }

    const observador = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (entrada) {
        if (!entrada.isIntersecting) return;

        entrada.target.classList.add("visivel");
        // Ja apareceu, nao precisa mais observar.
        observador.unobserve(entrada.target);
      });
    }, {
      // Comeca a animacao um pouco antes de encostar na borda
      rootMargin: "0px 0px -80px 0px",
      threshold: 0.08
    });

    alvos.forEach(function (el) {
      // Entrada em sequencia: cada irmao espera um pouco mais.
      // O limite de 5 evita que o ultimo item de uma lista grande
      // demore um tempo absurdo para aparecer.
      const irmaos = Array.from(el.parentElement.children).filter((f) => f.classList.contains("revelar"));
      const posicao = Math.min(irmaos.indexOf(el), 5);
      el.style.setProperty("--atraso", (posicao * 90) + "ms");

      observador.observe(el);
    });

    // REDE DE SEGURANCA: se passados 2,5 segundos existe elemento na
    // tela e NENHUM foi revelado, o observador nao esta funcionando
    // neste navegador. Mostra tudo de uma vez.
    // Conteudo que nao aparece e muito pior do que conteudo sem
    // animacao - e o visitante nem saberia que tem texto ali.
    setTimeout(function () {
      const algumNaTela = alvos.some(function (el) {
        const caixa = el.getBoundingClientRect();
        return caixa.top < window.innerHeight && caixa.bottom > 0;
      });
      const algumRevelado = alvos.some((el) => el.classList.contains("visivel"));

      if (algumNaTela && !algumRevelado) {
        alvos.forEach((el) => el.classList.add("visivel"));
      }
    }, 2500);
  }


  /* =================================================================
     6. BOTAO MAGNETICO
     -----------------------------------------------------------------
     O botao se desloca um pouco na direcao do cursor, como se
     fosse atraido. O segredo e o FATOR baixo: exagerar aqui deixa
     o efeito engracado em vez de elegante.
     ================================================================= */

  function botaoMagnetico() {
    if (menosMovimento) return;

    // So em telas com mouse de verdade. No celular nao faz sentido
    // e ainda atrapalharia o toque.
    if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;

    // 0.10 em vez de 0.22: o botao so "respira" na direcao do cursor.
    // Acima disso o efeito deixa de ser elegante e vira brincadeira.
    const FATOR = 0.10;
    const botoes = pegarTodos(".magnetico");

    botoes.forEach(function (botao) {
      botao.addEventListener("pointermove", function (evento) {
        const caixa = botao.getBoundingClientRect();
        // Distancia do cursor ate o CENTRO do botao
        const dx = evento.clientX - (caixa.left + caixa.width / 2);
        const dy = evento.clientY - (caixa.top + caixa.height / 2);
        botao.style.transform = "translate(" + (dx * FATOR) + "px, " + (dy * FATOR - 2) + "px)";
      });

      // Ao sair, limpa o transform e o CSS devolve o botao ao lugar
      // com a curva de mola.
      botao.addEventListener("pointerleave", function () {
        botao.style.transform = "";
      });
    });
  }


  /* =================================================================
     7. CONTADOR DE NUMEROS
     -----------------------------------------------------------------
     Um numero que sobe de 0 ate o valor final quando entra na tela.
     Funciona em qualquer elemento com data-contar="123.4".
     ================================================================= */

  function contarNumeros() {
    const alvos = pegarTodos("[data-contar]");
    if (!alvos.length) return;

    // Quantas casas decimais o numero original tem ("520.0" -> 1)
    const casasDe = (el) => (el.dataset.contar.split(".")[1] || "").length;

    function escrever(el, valor, casas) {
      el.textContent = valor.toLocaleString("pt-BR", {
        minimumFractionDigits: casas,
        maximumFractionDigits: casas
      });
    }

    function animar(el) {
      const destino = parseFloat(el.dataset.contar);
      if (isNaN(destino)) return;

      el.dataset.contado = "1";   // marca que a animacao comecou
      const casas = casasDe(el);
      const duracao = 1300;
      const inicio = performance.now();

      function passo(agora) {
        const t = Math.min((agora - inicio) / duracao, 1);
        // Ease out expo: comeca rapido e freia no final.
        const suave = t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
        escrever(el, destino * suave, casas);
        if (t < 1) requestAnimationFrame(passo);
      }

      requestAnimationFrame(passo);
    }

    // Sem suporte ou com movimento reduzido: mostra o numero certo
    // de uma vez, sem animacao nenhuma.
    if (menosMovimento || !("IntersectionObserver" in window)) {
      alvos.forEach((el) => escrever(el, parseFloat(el.dataset.contar), casasDe(el)));
      return;
    }

    const observador = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (entrada) {
        if (!entrada.isIntersecting) return;
        animar(entrada.target);
        observador.unobserve(entrada.target);
      });
    }, { threshold: 0.4 });

    alvos.forEach(function (el) {
      const caixa = el.getBoundingClientRect();
      const jaNaTela = caixa.top < window.innerHeight && caixa.bottom > 0;

      if (jaNaTela) {
        // REGRA IMPORTANTE: o numero ja visivel recebe o valor CERTO
        // antes de qualquer animacao. Se o navegador estiver com a aba
        // em segundo plano, se o rAF nao rodar ou se algo falhar, a
        // pessoa ve o numero verdadeiro - nunca um "0,0" mentiroso.
        escrever(el, parseFloat(el.dataset.contar), casasDe(el));
        animar(el);
      } else {
        // Abaixo da dobra: pode comecar em zero, porque so vai
        // aparecer depois que a pessoa rolar ate ele.
        escrever(el, 0, casasDe(el));
        observador.observe(el);

        // REDE DE SEGURANCA: se em 4 segundos a animacao nem comecou,
        // escreve o numero certo e desiste do efeito.
        // Isso cobre o caso raro em que o navegador congela o desenho
        // da pagina (aba em segundo plano, janela atras de outra) e o
        // observador nunca dispara. Um numero sem animacao e chato;
        // um zero no lugar do numero certo e informacao errada.
        setTimeout(function () {
          if (!el.dataset.contado) {
            escrever(el, parseFloat(el.dataset.contar), casasDe(el));
          }
        }, 4000);
      }
    });
  }


  /* =================================================================
     8. PARALLAX DAS PLANTAS
     -----------------------------------------------------------------
     As folhas sobem mais devagar que o resto da pagina, o que cria
     sensacao de profundidade. Cada planta tem a propria velocidade
     em data-parallax (ex.: 0.15 = anda 15% do scroll).
     ================================================================= */

  function parallaxPlantas() {
    if (menosMovimento) return;
    if (!window.matchMedia("(min-width: 700px)").matches) return;

    const plantas = pegarTodos("[data-parallax]");
    if (!plantas.length) return;

    let agendado = false;

    function atualizar() {
      const y = window.scrollY;
      plantas.forEach(function (planta) {
        const velocidade = parseFloat(planta.dataset.parallax) || 0.1;
        planta.style.setProperty("--deslocamento", (-y * velocidade).toFixed(1) + "px");
      });
      agendado = false;
    }

    window.addEventListener("scroll", function () {
      if (!agendado) {
        agendado = true;
        requestAnimationFrame(atualizar);
      }
    }, { passive: true });

    atualizar();
  }


  /* =================================================================
     9. AVISOS QUE SOMEM SOZINHOS
     ================================================================= */

  function avisosSomem() {
    const avisos = pegarTodos(".aviso");
    if (!avisos.length) return;

    function fechar(aviso) {
      aviso.classList.add("saindo");
      // Espera a animacao de saida terminar antes de remover
      setTimeout(() => aviso.remove(), 420);
    }

    avisos.forEach(function (aviso, indice) {
      // Botao de fechar manual
      const botao = aviso.querySelector(".fechar-aviso");
      if (botao) botao.addEventListener("click", () => fechar(aviso));

      // Some sozinho depois de 6 segundos (escalonado, para nao
      // sumirem todos no mesmo instante)
      setTimeout(() => {
        if (aviso.isConnected) fechar(aviso);
      }, 6000 + indice * 600);
    });
  }


  /* =================================================================
     LIGA TUDO
     ================================================================= */

  function iniciar() {
    menuCelular();
    aoRolar();
    voltarAoTopo();
    revelarNoScroll();
    botaoMagnetico();
    contarNumeros();
    parallaxPlantas();
    avisosSomem();
  }

  // Se o HTML ainda esta carregando, espera. Se ja carregou, roda ja.
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
