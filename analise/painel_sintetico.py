"""Painel veiculo x mes SINTETICO, com a mesma estrutura do painel real.

Serve para testar o pipeline sem nenhum dado da empresa. Os parametros
verdadeiros sao conhecidos, entao os testes conferem se os modelos os
recuperam. Nenhum numero daqui deve ser citado como resultado.

Estrutura gerada (uma linha por veiculo e mes):
    veiculo, site, mes, horas, milhas, frenagens, curvas, velocidade,
    acidentes (relatados), colisoes_detectadas, detectadas_e_relatadas
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass
class Parametros:
    n_sites: int = 40
    n_veiculos: int = 300
    n_meses: int = 14
    semente: int = 20261108
    # risco base: acidentes por hora de operacao
    taxa_base_hora: float = 0.0008
    # efeitos (log da taxa) por desvio padrao da taxa de evento
    beta: dict = field(default_factory=lambda: {
        "z_frenagens": 0.30,
        "z_curvas": 0.15,
        "z_velocidade": 0.00,  # efeito nulo de proposito (controle de H2)
    })
    dp_site: float = 0.40
    dp_veiculo: float = 0.30
    forma_gamma_nb: float = 2.0  # superdispersao extra (mistura gamma)
    prob_deteccao: float = 0.35  # chance de o sensor detectar um acidente
    relato_medio: float = 0.65  # probabilidade media de relato
    relato_concentracao: float = 8.0  # Beta(a, b) com a + b = concentracao
    prob_troca_site: float = 0.05


def gerar(p: Parametros | None = None) -> tuple[pd.DataFrame, dict]:
    """Devolve (painel, verdade), em que verdade guarda os parametros reais."""
    p = p or Parametros()
    rng = np.random.default_rng(p.semente)

    # tamanho dos sites desigual (poucos sites grandes, muitos pequenos)
    peso_site = rng.lognormal(0, 1.0, p.n_sites)
    site_inicial = rng.choice(p.n_sites, p.n_veiculos, p=peso_site / peso_site.sum())
    troca = rng.random(p.n_veiculos) < p.prob_troca_site
    mes_troca = rng.integers(1, p.n_meses, p.n_veiculos)
    site_novo = rng.integers(0, p.n_sites, p.n_veiculos)

    u_site = rng.normal(0, p.dp_site, p.n_sites)
    v_veic = rng.normal(0, p.dp_veiculo, p.n_veiculos)
    p_relato = rng.beta(p.relato_medio * p.relato_concentracao,
                        (1 - p.relato_medio) * p.relato_concentracao, p.n_sites)

    # taxas de eventos por 100 h: nivel do veiculo + ruido mensal
    nivel = {k: rng.lognormal(0, 0.5, p.n_veiculos) for k in ("frenagens", "curvas", "velocidade")}
    base_eventos = {"frenagens": 3.0, "curvas": 2.0, "velocidade": 1.0}

    linhas = []
    for i in range(p.n_veiculos):
        atividade = rng.gamma(4, 1 / 4)
        for t in range(p.n_meses):
            s = site_novo[i] if (troca[i] and t >= mes_troca[i]) else site_inicial[i]
            horas = rng.gamma(4, 150 * atividade / 4)
            milhas = horas * rng.uniform(2.0, 4.0)
            ev = {k: rng.poisson(base_eventos[k] * nivel[k][i] * horas / 100) for k in nivel}
            linhas.append(dict(veiculo=f"V{i:03d}", site=f"S{s:02d}", mes=t, horas=horas,
                               milhas=milhas, **ev, _s=s, _i=i))
    df = pd.DataFrame(linhas)

    # covariaveis padronizadas (taxa por 100 h, em escala log)
    for k in ("frenagens", "curvas", "velocidade"):
        taxa = np.log((df[k] + 0.5) / df["horas"] * 100)
        df[f"z_{k}"] = (taxa - taxa.mean()) / taxa.std()

    eta = (np.log(p.taxa_base_hora) + np.log(df["horas"])
           + sum(b * df[c] for c, b in p.beta.items())
           + u_site[df["_s"]] + v_veic[df["_i"]])
    mu = np.exp(eta) * rng.gamma(p.forma_gamma_nb, 1 / p.forma_gamma_nb, len(df))
    verdadeiros = rng.poisson(mu)

    detectados = rng.binomial(verdadeiros, p.prob_deteccao)
    nao_detectados = verdadeiros - detectados
    pr = p_relato[df["_s"]]
    det_e_rel = rng.binomial(detectados, pr)
    df["acidentes"] = det_e_rel + rng.binomial(nao_detectados, pr)
    df["colisoes_detectadas"] = detectados
    df["detectadas_e_relatadas"] = det_e_rel

    verdade = dict(
        beta=p.beta,
        u_site={f"S{s:02d}": u for s, u in enumerate(u_site)},
        p_relato={f"S{s:02d}": q for s, q in enumerate(p_relato)},
        acidentes_verdadeiros=int(verdadeiros.sum()),
    )
    return df.drop(columns=["_s", "_i"]), verdade


if __name__ == "__main__":
    painel, verdade = gerar()
    print(painel.describe().T.round(2))
    print("acidentes relatados:", painel["acidentes"].sum(),
          "| verdadeiros:", verdade["acidentes_verdadeiros"])
