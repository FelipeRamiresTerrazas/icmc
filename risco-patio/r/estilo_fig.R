# Estilo comum das figuras (R). Espelha analise/estilo_fig.py: mesmos papeis de cor,
# mesmos sufixos de arquivo (nome.pdf, nome_en.pdf, nome_pb.pdf, nome_en_pb.pdf).
# No LaTeX, \arqfig{nome} escolhe o arquivo pela lingua e pelo modo do documento.

LARGURA <- 6.3
MODOS <- c("cor", "pb")

PALETAS <- list(
  cor = list(principal = "#1F3A5F", secundaria = "#D55E00", terciaria = "#009E73", quaternaria = "#E69F00",
             barra = "#4A6F96", clara = "#A9BDD4", caixa = "#D3DEEA", pontos = "#1F3A5F", faixa = "#CCD9E8",
             destaque = "#C0392B", neutro = "#9AA5B1", linha = "black", referencia = "grey50",
             div_baixo = "#D55E00", div_alto = "#1F3A5F"),
  pb = list(principal = "grey15", secundaria = "grey50", terciaria = "grey75", quaternaria = "grey90",
            barra = "grey55", clara = "grey80", caixa = "grey87", pontos = "grey35", faixa = "grey85",
            destaque = "black", neutro = "grey62", linha = "black", referencia = "grey50",
            div_baixo = "grey30", div_alto = "black")
)

sufixo_fig <- function(lang, modo) paste0(if (lang == 1) "_en" else "", if (modo == "pb") "_pb" else "")

variantes <- function() expand.grid(lang = 0:1, modo = MODOS, stringsAsFactors = FALSE)
