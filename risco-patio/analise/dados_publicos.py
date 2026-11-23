"""Datasets publicos usados como banco de testes (sem dados da empresa).

Hoje: "Logistics Operations Database" (Kaggle, yogape, licenca MIT), uma
transportadora FICTICIA de 2022 a 2024 com tabela caminhao x mes (milhas) e
incidentes de seguranca. Serve para exercitar o pipeline num painel com a
mesma forma do real: caminhao x mes, exposicao em milhas, unidade = terminal.

Uso (na raiz do repositorio):
    .venv/Scripts/python analise/dados_publicos.py baixar   # ~15 MB zipado
    PYTHONIOENCODING=utf-8 .venv/Scripts/python analise/dados_publicos.py exemplo

Os CSVs ficam em dados/publicos/ (fora do git). Ver notas/05-datasets-publicos.md.
"""

from __future__ import annotations

import io
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
PASTA = RAIZ / "dados" / "publicos" / "logistics-operations-database"
URL = "https://www.kaggle.com/api/v1/datasets/download/yogape/logistics-operations-database"

# Tipos de incidente tratados como "acidente" (desfecho principal); os demais
# (violacoes, reclamacoes) entram so na definicao alternativa.
TIPOS_ACIDENTE = ("Accident", "Equipment Damage")


def baixar(destino: Path = PASTA) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL) as r:  # a API redireciona para o arquivo zip
        conteudo = r.read()
    zipfile.ZipFile(io.BytesIO(conteudo)).extractall(destino)
    print(f"{len(conteudo) / 1e6:.1f} MB extraidos em {destino}")


def montar_painel(pasta: Path = PASTA, tipos: tuple[str, ...] | None = TIPOS_ACIDENTE) -> pd.DataFrame:
    """Painel caminhao x mes no formato de analise/modelos.py.

    Colunas: veiculo, site (terminal de origem), mes (0, 1, ...), milhas,
    viagens, acidentes, z_idade, z_manutencao, z_parada.
    tipos=None conta todos os incidentes.
    """
    util = pd.read_csv(pasta / "truck_utilization_metrics.csv", parse_dates=["month"])
    caminhoes = pd.read_csv(pasta / "trucks.csv")
    inc = pd.read_csv(pasta / "safety_incidents.csv", parse_dates=["incident_date"])
    if tipos is not None:
        inc = inc[inc["incident_type"].isin(tipos)]
    inc["month"] = inc["incident_date"].dt.to_period("M").dt.to_timestamp()
    contagem = inc.groupby(["truck_id", "month"]).size().rename("acidentes")

    df = (util.merge(caminhoes[["truck_id", "home_terminal", "model_year"]], on="truck_id", how="left")
              .merge(contagem, on=["truck_id", "month"], how="left"))
    df["acidentes"] = df["acidentes"].fillna(0).astype(int)
    df = df[df["total_miles"] > 0].copy()
    meses = sorted(df["month"].unique())
    df["mes"] = df["month"].map({m: i for i, m in enumerate(meses)})
    df["idade"] = df["month"].dt.year - df["model_year"]
    for origem, z in (("idade", "z_idade"), ("maintenance_events", "z_manutencao"), ("downtime_hours", "z_parada")):
        df[z] = (df[origem] - df[origem].mean()) / df[origem].std()
    return df.rename(columns={"truck_id": "veiculo", "home_terminal": "site", "total_miles": "milhas",
                              "trips_completed": "viagens"})[
        ["veiculo", "site", "mes", "month", "milhas", "viagens", "acidentes", "z_idade", "z_manutencao", "z_parada"]]


def exemplo() -> None:
    sys.path.insert(0, str(Path(__file__).parent))
    import modelos

    df = montar_painel()
    print(f"painel: {len(df)} caminhao-mes, {df['veiculo'].nunique()} caminhoes, {df['site'].nunique()} terminais, "
          f"{df['acidentes'].sum()} acidentes ({', '.join(TIPOS_ACIDENTE)})")
    print("distribuicao de acidentes por caminhao-mes:", df["acidentes"].value_counts().sort_index().to_dict())
    print(f"media {df['acidentes'].mean():.4f}, variancia {df['acidentes'].var():.4f}")

    cov = ["z_idade", "z_manutencao", "z_parada"]
    res = modelos.ajustar(df, "nb", cov, com_site=True, exposicao="milhas")
    print("\nNB com milhas como offset (coef. | IC 95%):")
    for c in cov:
        lo, hi = res.conf_int().loc[c]
        print(f"  {c:13s} {res.params[c]:+.3f} [{lo:+.3f}, {hi:+.3f}]")
    print(f"  alpha {res.params['alpha']:.3f}")

    print("\nvalidacao temporal (ultimos 6 meses):")
    print(modelos.validacao_temporal(df, 6, exposicao="milhas", covariaveis=cov).round(4).to_string(index=False))
    print("\nindicadores por terminal entre metades (erro por milhao de milhas):")
    print(modelos.estabilidade_rankings(df, exposicao="milhas", escala=1e6).round(3).to_string(index=False))

    # Teste de sanidade do proprio dataset: a taxa depende da exposicao?
    g = df.assign(q=pd.qcut(df["milhas"], 4, labels=["Q1", "Q2", "Q3", "Q4"]))
    t = g.groupby("q", observed=True).agg(acid=("acidentes", "sum"), milhas=("milhas", "sum"), n=("acidentes", "size"))
    t["por_mes"] = t["acid"] / t["n"]
    t["por_milhao_milhas"] = t["acid"] / t["milhas"] * 1e6
    print("\nacidentes por quartil de milhas no mes (o gerador do dataset liga risco a exposicao?):")
    print(t.round(3).to_string())


if __name__ == "__main__":
    acao = sys.argv[1] if len(sys.argv) > 1 else "exemplo"
    {"baixar": baixar, "exemplo": exemplo}[acao]()
