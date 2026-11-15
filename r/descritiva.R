# Capitulo de analise descritiva: figuras que dependem de modelo de contagem.
# So valores relativos (proporcoes, razoes, correlacoes): podem entrar no texto.
#
# Entrada: ../resultados/real/painel_h2.csv (gerado por analise/real/testes.py)
# Saidas:  ../dissertacao/figuras/fig_desc_contagem[_en].pdf
#          ../dissertacao/figuras/fig_desc_eventos[_en].pdf
#          ../dissertacao/tabelas/num_descritiva_r.tex (macros citadas no texto)
# Uso (dentro de r/):  Rscript descritiva.R

suppressPackageStartupMessages({
  library(glmmTMB)
  library(ggplot2)
  library(cowplot)
  library(scales)
})
source("estilo_fig.R")
set.seed(20261115)

d <- read.csv("../resultados/real/painel_h2.csv")
d$vehicle_id <- factor(d$vehicle_id)
d$uso <- relevel(factor(d$uso), ref = "Spot Tractor")
d$off <- log(d$horas / 100)
FIG <- "../dissertacao/figuras"
NSIM <- 300

rotulos <- c(Braking = "frenagem brusca|harsh braking", HarshTurn = "curva brusca|harsh turn",
             FollowingDistance = "seguir de perto|following distance", MaxSpeed = "acima do limite|over speed limit",
             SevereSpeeding = "excesso grave|severe speeding", MobileUsage = "uso de celular|phone use",
             GenericDistraction = "distração|distraction", RollingStop = "parada incompleta|rolling stop",
             NoSeatbelt = "sem cinto|no seatbelt", Drowsy = "sonolência|drowsiness")
rot <- function(chave, lang) sapply(strsplit(rotulos[chave], "\\|"), `[`, lang + 1)
tr <- function(lang, pt, en) if (lang == 0) pt else en
num <- function(lang, acc = NULL) label_number(accuracy = acc, decimal.mark = tr(lang, ",", "."), big.mark = "")

# ------------------------------------------------------------ modelos
m_poi <- glmmTMB(acid ~ uso + offset(off), data = d, family = poisson)
m_nb <- glmmTMB(acid ~ uso + offset(off), data = d, family = nbinom2)
m_re <- glmmTMB(acid ~ uso + (1 | vehicle_id) + offset(off), data = d, family = nbinom2)

cats <- function(y) table(factor(pmin(y, 3), levels = 0:3)) / length(y)
freq_sim <- function(m) rowMeans(sapply(simulate(m, nsim = NSIM), cats))
f_obs <- as.numeric(cats(d$acid))
f_mod <- list(poi = freq_sim(m_poi), nb = freq_sim(m_nb), re = freq_sim(m_re))

tot_cats <- function(y) table(factor(pmin(tapply(y, d$vehicle_id, sum), 5), levels = 0:5)) / nlevels(d$vehicle_id)
tot_sim <- function(m) rowMeans(sapply(simulate(m, nsim = NSIM), tot_cats))
t_obs <- as.numeric(tot_cats(d$acid))
t_mod <- list(poi = tot_sim(m_poi), re = tot_sim(m_re))

re <- as.data.frame(ranef(m_re))
re <- re[order(re$condval), ]
re$x <- seq(0, 1, length.out = nrow(re))

# ------------------------------------------------------------ eventos
taxas <- sapply(names(rotulos), function(k) d[[k]] / d$horas * 100)
cor_m <- cor(cbind(taxas, acid = d$acid / d$horas * 100, horas = d$horas), method = "spearman")

tema <- theme_classic(base_size = 8, base_family = "serif") +
  theme(plot.title = element_text(size = 8.5, hjust = 0.5), legend.position = "bottom",
        legend.title = element_blank(), legend.key.size = unit(0.3, "cm"))

v <- variantes()
for (i in seq_len(nrow(v))) {
  lang <- v$lang[i]
  modo <- v$modo[i]
  P <- PALETAS[[modo]]
  suf <- sufixo_fig(lang, modo)
  nomes_m <- c(obs = tr(lang, "observado", "observed"), poi = "Poisson", nb = tr(lang, "binomial negativa", "negative binomial"),
               re = tr(lang, "BN + efeito de veículo", "NB + vehicle effect"))

  # (a) veiculo-mes
  ka <- c("0", "1", "2", "3+")
  da <- data.frame(k = factor(rep(ka, 3), levels = ka), modelo = rep(c("poi", "nb", "re"), each = 4),
                   f = c(f_mod$poi, f_mod$nb, f_mod$re))
  da$modelo <- factor(nomes_m[da$modelo], levels = nomes_m[c("poi", "nb", "re")])
  pa <- ggplot() +
    geom_col(data = data.frame(k = factor(ka, levels = ka), f = f_obs), aes(k, f), fill = P$clara, colour = "black",
             linewidth = 0.2, width = 0.7) +
    geom_point(data = da, aes(k, f, shape = modelo, colour = modelo), position = position_dodge(width = 0.5), size = 1.6) +
    scale_y_sqrt(labels = num(lang, 0.01), breaks = c(0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 1)) +
    scale_shape_manual(values = c(1, 2, 16)) +
    scale_colour_manual(values = c(P$secundaria, P$terciaria, P$principal)) +
    labs(x = tr(lang, "acidentes no veículo-mês", "accidents per vehicle-month"),
         y = tr(lang, "proporção (escala raiz)", "proportion (square-root scale)"),
         title = tr(lang, "(a) Veículo-mês", "(a) Vehicle-month")) +
    tema + guides(shape = guide_legend(nrow = 3))

  # (b) total por veiculo
  kb <- c("0", "1", "2", "3", "4", "5+")
  db <- data.frame(k = factor(rep(kb, 2), levels = kb), modelo = rep(c("poi", "re"), each = 6), f = c(t_mod$poi, t_mod$re))
  db$modelo <- factor(nomes_m[db$modelo], levels = nomes_m[c("poi", "re")])
  pb <- ggplot() +
    geom_col(data = data.frame(k = factor(kb, levels = kb), f = t_obs), aes(k, f), fill = P$clara, colour = "black",
             linewidth = 0.2, width = 0.7) +
    geom_point(data = db, aes(k, f, shape = modelo, colour = modelo), position = position_dodge(width = 0.5), size = 1.6) +
    scale_y_sqrt(labels = num(lang, 0.01), breaks = c(0.01, 0.05, 0.1, 0.25, 0.5)) +
    scale_shape_manual(values = c(1, 16)) +
    scale_colour_manual(values = c(P$secundaria, P$principal)) +
    labs(x = tr(lang, "acidentes do veículo no período", "accidents per vehicle in the period"),
         y = NULL, title = tr(lang, "(b) Total por veículo", "(b) Total per vehicle")) +
    tema + guides(shape = guide_legend(nrow = 3))

  # (c) efeitos de veiculo
  pc <- ggplot(re, aes(x, exp(condval))) +
    geom_hline(yintercept = 1, linetype = "dotted", colour = "grey50") +
    geom_linerange(aes(ymin = exp(condval - 1.96 * condsd), ymax = exp(condval + 1.96 * condsd)), colour = P$neutro,
                   linewidth = 0.25) +
    geom_point(size = 0.5, colour = P$principal) +
    scale_y_log10(labels = num(lang), breaks = c(0.25, 0.5, 1, 2, 4)) +
    labs(x = tr(lang, "veículos ordenados", "vehicles in order"),
         y = tr(lang, "risco relativo do veículo (IC 95%)", "vehicle relative risk (95% CI)"),
         title = tr(lang, "(c) Efeito de veículo", "(c) Vehicle effect")) +
    tema + theme(axis.text.x = element_blank(), axis.ticks.x = element_blank())

  g1 <- plot_grid(pa, pb, pc, nrow = 1, rel_widths = c(1.1, 1, 1), align = "h", axis = "b")
  ggsave(file.path(FIG, paste0("fig_desc_contagem", suf, ".pdf")), g1, width = 6.3, height = 2.9, device = cairo_pdf)

  # eventos: (a) distribuicao das taxas
  algum <- colMeans(taxas > 0, na.rm = TRUE)
  ordem <- names(sort(algum))
  de <- data.frame(ev = factor(ordem, levels = ordem, labels = rot(ordem, lang)), p = 100 * algum[ordem])
  pe <- ggplot(de, aes(p, ev)) +
    geom_col(fill = P$barra, colour = "black", linewidth = 0.2, width = 0.65) +
    scale_x_continuous(labels = num(lang), limits = c(0, 100), expand = c(0, 0)) +
    labs(x = tr(lang, "% dos veículo-meses com o evento", "% of vehicle-months with the event"),
         y = NULL, title = tr(lang, "(a) Frequência dos eventos", "(a) Event frequency")) + tema

  # (b) correlacoes de Spearman
  nm <- c(rot(names(rotulos), lang), tr(lang, "acidentes / h", "accidents / h"), tr(lang, "horas", "hours"))
  dc <- as.data.frame(as.table(cor_m))
  lev <- c(ordem, "acid", "horas")
  dc$Var1 <- factor(dc$Var1, levels = lev, labels = nm[match(lev, colnames(cor_m))])
  dc$Var2 <- factor(dc$Var2, levels = rev(lev), labels = rev(nm[match(lev, colnames(cor_m))]))
  pf <- ggplot(dc, aes(Var1, Var2, fill = Freq)) +
    geom_tile(colour = "white", linewidth = 0.2) +
    geom_text(aes(label = num(lang, 0.1)(Freq)), size = 1.8,
              family = "serif", colour = ifelse(abs(dc$Freq) > 0.55, "white", "black")) +
    scale_fill_gradient2(low = P$div_baixo, mid = "white", high = P$div_alto, limits = c(-1, 1), labels = num(lang)) +
    labs(x = NULL, y = NULL, title = tr(lang, "(b) Correlação de Spearman", "(b) Spearman correlation")) +
    tema + theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 6.5), axis.text.y = element_text(size = 6.5),
                 legend.position = "right",
                 legend.key.height = unit(0.6, "cm"), axis.line = element_blank(), axis.ticks = element_blank())

  g2 <- plot_grid(pe, pf, nrow = 1, rel_widths = c(1, 1.35))
  ggsave(file.path(FIG, paste0("fig_desc_eventos", suf, ".pdf")), g2, width = 6.3, height = 3.3, device = cairo_pdf)
}

# ------------------------------------------------------------ macros
fmt <- function(x, casas) sprintf("\\tr{%s}{%s}", sub(".", ",", sprintf(paste0("%.", casas, "f"), x), fixed = TRUE),
                                   sprintf(paste0("%.", casas, "f"), x))
ev_cor <- cor_m[names(rotulos), names(rotulos)]
diag(ev_cor) <- NA
macros <- c(
  descRzerosObs = fmt(100 * f_obs[1], 0), descRzerosPoisson = fmt(100 * f_mod$poi[1], 0),
  descRzerosNB = fmt(100 * f_mod$nb[1], 0), descRzerosRE = fmt(100 * f_mod$re[1], 0),
  descRveicZeroObs = fmt(100 * t_obs[1], 0), descRveicZeroPoisson = fmt(100 * t_mod$poi[1], 0),
  descRveicZeroRE = fmt(100 * t_mod$re[1], 0),
  descRdpVeiculo = fmt(sqrt(VarCorr(m_re)$cond$vehicle_id[1]), 2),
  descRcorMax = fmt(max(abs(ev_cor), na.rm = TRUE), 2),
  descRcorAcidMax = fmt(max(abs(cor_m[names(rotulos), "acid"])), 2),
  descRcorHorasMax = fmt(max(abs(cor_m[names(rotulos), "horas"])), 2)
)
writeLines(c("% Gerado por r/descritiva.R: nao editar a mao.",
             sprintf("\\newcommand{\\%s}{%s}", names(macros), macros)),
           "../dissertacao/tabelas/num_descritiva_r.tex", useBytes = TRUE)
print(macros)
cat("ok\n")
