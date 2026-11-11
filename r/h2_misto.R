# H2 com modelo misto (uso interno): binomial negativa (NB2) com efeito aleatorio
# de veiculo, offset log(horas de viagem) e tipo de uso como covariavel.
# Para cada rotulo de telemetria: IRR por 1 DP, IC 95%, IC 90% (TOST) e Holm.
# H0 de igualdade: IRR = 1. Equivalencia (TOST, alfa 5%): IC 90% dentro de [0,8; 1,25].
#
# Entrada: ../resultados/real/painel_h2.csv (gerado por analise/real/testes.py)
# Saida:   ../resultados/real/h2_misto.csv e h2_base.txt
# Uso (dentro de r/):  Rscript h2_misto.R

suppressPackageStartupMessages({
  library(glmmTMB)
  library(DHARMa)
})
set.seed(20261111)

ent <- "../resultados/real/painel_h2.csv"
d <- read.csv(ent)
d$vehicle_id <- factor(d$vehicle_id)
d$uso <- relevel(factor(d$uso), ref = "Spot Tractor")
d$off <- log(d$horas / 100)

rotulos <- c("Braking", "HarshTurn", "FollowingDistance", "MaxSpeed", "SevereSpeeding",
             "MobileUsage", "GenericDistraction", "RollingStop", "NoSeatbelt", "Drowsy")
margem <- c(0.8, 1.25)

ajusta <- function(f) glmmTMB(f, data = d, family = nbinom2)

base <- ajusta(acid ~ uso + (1 | vehicle_id) + offset(off))
sem_re <- ajusta(acid ~ uso + offset(off))
sim <- simulateResiduals(base, n = 1000)
saida_base <- c(
  sprintf("veiculo-meses: %d; veiculos: %d; acidentes: %d", nrow(d), nlevels(d$vehicle_id), sum(d$acid)),
  sprintf("DP do efeito aleatorio de veiculo (escala log): %.3f", sqrt(VarCorr(base)$cond$vehicle_id[1])),
  sprintf("theta NB2 (com efeito aleatorio): %.3f", sigma(base)),
  sprintf("theta NB2 (sem efeito aleatorio): %.3f", sigma(sem_re)),
  sprintf("AIC com / sem efeito aleatorio: %.1f / %.1f", AIC(base), AIC(sem_re)),
  sprintf("TRV do efeito aleatorio: chi2 = %.2f, p (mistura 50:50) = %.4f",
          2 * (logLik(base) - logLik(sem_re)), 0.5 * pchisq(2 * as.numeric(logLik(base) - logLik(sem_re)), 1, lower.tail = FALSE)),
  sprintf("DHARMa dispersao: p = %.3f; inflacao de zeros: p = %.3f; uniformidade (KS): p = %.3f",
          testDispersion(sim, plot = FALSE)$p.value, testZeroInflation(sim, plot = FALSE)$p.value,
          testUniformity(sim, plot = FALSE)$p.value),
  "IRR do tipo de uso (referencia: spot):",
  capture.output(print(round(exp(cbind(IRR = fixef(base)$cond, confint(base, parm = "beta_")[, 1:2])), 3)))
)
writeLines(saida_base, "../resultados/real/h2_base.txt")
cat(saida_base, sep = "\n")

linhas <- list()
for (r in rotulos) {
  z <- paste0("z_", r)
  for (modelo in c("bruto", "ajustado")) {
    f <- if (modelo == "bruto") as.formula(paste("acid ~", z, "+ offset(off)"))
         else as.formula(paste("acid ~", z, "+ uso + (1 | vehicle_id) + offset(off)"))
    m <- ajusta(f)
    s <- summary(m)$coefficients$cond[z, ]
    b <- s["Estimate"]; se <- s["Std. Error"]
    linhas[[length(linhas) + 1]] <- data.frame(
      rotulo = r, modelo = modelo, irr = exp(b),
      ic95_lo = exp(b - 1.96 * se), ic95_hi = exp(b + 1.96 * se),
      ic90_lo = exp(b - 1.645 * se), ic90_hi = exp(b + 1.645 * se),
      p = s["Pr(>|z|)"])
  }
}
res <- do.call(rbind, linhas)
res$p_holm <- NA
for (mm in unique(res$modelo)) {
  i <- res$modelo == mm
  res$p_holm[i] <- p.adjust(res$p[i], method = "holm")
}
res$equivalente <- res$ic90_lo > margem[1] & res$ic90_hi < margem[2]
res$conclusao <- ifelse(res$p_holm < 0.05, "rejeita H0 (IRR diferente de 1)",
                 ifelse(res$equivalente, "equivalente a nulo (dentro de 0,8 a 1,25)", "inconclusivo"))
write.csv(res, "../resultados/real/h2_misto.csv", row.names = FALSE)
print(format(res, digits = 3), row.names = FALSE)
