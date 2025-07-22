document.addEventListener("DOMContentLoaded", () => {
    const garagesContainer = document.getElementById("garages-container");
    const btnAddGarage = document.getElementById("btnAddGarage");
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    function setupCarrossel(bloco) {
        const carrosselWrapper = bloco.querySelector(".carrossel-wrapper");
        const leftArrow = bloco.querySelector(".left-arrow");
        const rightArrow = bloco.querySelector(".right-arrow");

        if (!carrosselWrapper || !leftArrow || !rightArrow) return;

        leftArrow.addEventListener("click", () => {
            carrosselWrapper.scrollBy({ left: -300, behavior: "smooth" });
        });

        rightArrow.addEventListener("click", () => {
            carrosselWrapper.scrollBy({ left: 300, behavior: "smooth" });
        });
    }

    function setupComentario(bloco) {
        const abrirComentario = bloco.querySelector(".abrir-comentario");
        const painelComentario = bloco.querySelector(".painel-comentario");
        const fecharComentario = bloco.querySelector(".fechar-comentario");
        const textarea = bloco.querySelector(".textarea-comentario");

        if (!abrirComentario || !painelComentario || !fecharComentario) return;

        // Função pra atualizar o texto do botão abrirComentario dependendo do conteúdo do textarea
        function atualizarTextoBotao() {
            if (textarea.value.trim().length > 0) {
                abrirComentario.textContent = "Sobre a garagem";
            } else {
                abrirComentario.textContent = "Adicione um comentário sobre";
            }
        }

        // Atualiza o texto ao carregar o bloco, baseado no conteúdo do textarea (se já tem comentário)
        atualizarTextoBotao();

        abrirComentario.addEventListener("click", () => {
            painelComentario.style.display = "block";
            abrirComentario.textContent = "Sobre a garagem";
        });

        fecharComentario.addEventListener("click", () => {
            painelComentario.style.display = "none";
            atualizarTextoBotao();
        });
    }

    function setupConfirmarComentario(btn, bloco) {
        btn.addEventListener("click", () => {
            const garagemId = btn.dataset.garagemId;
            const textarea = bloco.querySelector(".textarea-comentario");
            const texto = textarea.value;

            fetch("/salvar_comentario", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": csrfToken
                },
                body: `garagem_id=${garagemId}&texto=${encodeURIComponent(texto)}`,
            })
            .then((res) => res.json())
            .then((data) => {
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    alert("Comentário salvo!");
                    // Atualiza o texto do botão após salvar
                    const abrirComentario = bloco.querySelector(".abrir-comentario");
                    if (texto.trim().length > 0) {
                        abrirComentario.textContent = "Sobre a garagem";
                    } else {
                        abrirComentario.textContent = "Adicione um comentário sobre";
                    }
                    // Fecha o painel depois de salvar (opcional)
                    bloco.querySelector(".painel-comentario").style.display = "none";
                }
            });
        });
    }


    // Setup inicial para blocos existentes
    document.querySelectorAll(".garagem-bloco").forEach((bloco) => {
        setupCarrossel(bloco);
        setupComentario(bloco);
        const btn = bloco.querySelector(".btn-confirmar");
        if (btn) setupConfirmarComentario(btn, bloco);
    });

    // Botão para adicionar nova garagem
    if (btnAddGarage && garagesContainer) {
        btnAddGarage.addEventListener("click", () => {
            fetch('/adicionar_garagem', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({})
            })
            .then(async res => {
                const text = await res.text();
                try {
                    const data = JSON.parse(text);
                    if (!data.id) throw new Error('ID da garagem não retornado');
                    return data;
                } catch {
                    throw new Error('Resposta não é JSON: ' + text);
                }
            })
            .then(data => {
                const garagemId = data.id;
                const novoBloco = document.createElement("div");
                novoBloco.classList.add("garagem-bloco");

                novoBloco.innerHTML = `
                  <div class="carrossel-header">
                    <img src="/static/imagens/garage.png" class="garage">
                    <a href="/adicionar_carro/${garagemId}">
                      <p class="novo-carro-text">Novo carro +</p>
                    </a>
                  </div>

                  <div class="carrossel-container">
                    <img src="/static/imagens/arrow_left.png" class="arrow left-arrow">
                    <div class="carrossel-wrapper">
                      <div class="carrossel-content">
                      </div>
                    </div>
                    <img src="/static/imagens/arrow_right.png" class="arrow right-arrow">
                  </div>

                  <form method="POST" action="/excluir_garagem/${garagemId}">
                    <input type="hidden" name="csrf_token" value="${csrfToken}">
                    <button type="submit" class="btn-excluir">Excluir garagem</button>
                  </form>

                  <p class="add-text comentario-texto abrir-comentario">Adicione um comentário sobre</p>

                  <div class="painel-comentario" style="display:none;">
                    <div class="painel-topo">
                      <img src="/static/imagens/back.png" class="btn-voltar fechar-comentario">
                      <span class="titulo-painel">Sobre a garagem</span>
                    </div>

                    <textarea class="textarea-comentario" placeholder="Digite seu comentário..."></textarea>

                    <button class="btn-confirmar" data-garagem-id="${garagemId}">Confirmar</button>
                  </div>
                `;

                garagesContainer.appendChild(novoBloco);

                setupCarrossel(novoBloco);
                setupComentario(novoBloco);
                const btnConfirmar = novoBloco.querySelector(".btn-confirmar");
                if (btnConfirmar) setupConfirmarComentario(btnConfirmar, novoBloco);
            })
            .catch((err) => {
                console.error("Erro ao criar garagem:", err);
                alert("Erro ao criar garagem. Veja console.");
            });
        });
    }
});



const inputTrocarImagem = document.getElementById("inputTrocarImagem");
let carroIdSelecionado = null;
let imgClicada = null;

const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Clique em qualquer parte do carro (div.carrossel-item)
document.querySelectorAll(".carrossel-item").forEach((item) => {
  item.addEventListener("click", (event) => {
    const img = item.querySelector("img");
    if (!img) return;

    carroIdSelecionado = img.dataset.carroId;
    imgClicada = img;
    inputTrocarImagem.click();
  });
});

// Quando selecionar uma imagem para trocar
inputTrocarImagem.addEventListener("change", (event) => {
  const arquivo = event.target.files[0];
  if (!arquivo || !carroIdSelecionado) return;

  const formData = new FormData();
  formData.append('imagem', arquivo);

  fetch(`/upload_carro/${carroIdSelecionado}`, {
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRFToken': csrfToken
    }
  })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        alert(data.error);
        return;
      }
      // Atualizar a imagem no carrossel
      if (imgClicada) {
        imgClicada.src = data.imagem_url;
      }
      inputTrocarImagem.value = "";
    })
    .catch(err => {
      console.error("Erro ao trocar imagem:", err);
      alert("Erro ao trocar imagem do carro.");
    });
});











