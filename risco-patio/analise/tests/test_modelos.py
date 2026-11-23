"""Testes do esqueleto com o painel sintetico (parametros conhecidos)."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import modelos  # noqa: E402
import painel_sintetico  # noqa: E402

PAINEL, VERDADE = painel_sintetico.gerar()


def test_estrutura_do_painel():
    p = painel_sintetico.Parametros()
    assert len(PAINEL) == p.n_veiculos * p.n_meses
    assert (PAINEL["detectadas_e_relatadas"] <= PAINEL["colisoes_detectadas"]).all()
    assert (PAINEL["detectadas_e_relatadas"] <= PAINEL["acidentes"]).all()


def test_nb_recupera_efeito_de_frenagem():
    res = modelos.ajustar(PAINEL, "nb", modelos.COVARIAVEIS_TELEMETRIA)
    lo, hi = res.conf_int().loc["z_frenagens"]
    assert lo < VERDADE["beta"]["z_frenagens"] < hi
    assert lo > 0  # efeito positivo detectado


def test_bayes_empirico_encolhe_para_a_media():
    g = PAINEL.groupby("site").agg(y=("acidentes", "sum"), e=("horas", "sum"))
    eb = modelos.taxa_bayes_empirico(g["y"], g["e"])
    m = g["y"].sum() / g["e"].sum()
    assert ((eb["taxa_eb"] - m).abs() <= (eb["taxa_bruta"] - m).abs() + 1e-12).all()


def test_probabilidade_de_relato_perto_da_verdadeira():
    rel = modelos.probabilidade_relato(PAINEL)
    verdade = np.mean(list(VERDADE["p_relato"].values()))
    assert abs(rel.attrs["p_media"] - verdade) < 0.1
