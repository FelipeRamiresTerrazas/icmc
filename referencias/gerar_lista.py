"""Gera a lista de leitura em PDF a partir do ../referencias.bib.

Uso (dentro de referencias/):
    python gerar_lista.py
    TEXINPUTS=".;../;" latexmk -pdf -jobname=Lista_de_Leitura lista_leitura.tex

Cada referencia aparece no tema dela, com a citacao completa, o motivo para
ler e um link (DOI, URL ou busca no Google Scholar). Para incluir uma
referencia nova, acrescente a chave em TEMAS abaixo (as que ficarem de fora
aparecem no fim, em "Sem tema").
"""

import re
import urllib.parse
from pathlib import Path

AQUI = Path(__file__).parent
BIB = AQUI.parent / "referencias.bib"

# (titulo do tema, [(chave, por que ler)])
TEMAS = [
    ("Comece por aqui", [
        ("cai2021", "Método quase igual ao do projeto (binomial negativa bayesiana, milhas como exposição, telemetria de caminhões)."),
        ("filom2022", "Mapa do ML em pátios portuários, o parente mais próximo de pátio que tem literatura."),
        ("lord2010", "Referência básica sobre modelos de frequência de acidentes."),
        ("rosenman2006", "Captura e recaptura aplicada a lesões de trabalho: base da etapa de subnotificação."),
    ]),
    ("ML e analytics em logística e cadeia de suprimentos", [
        ("akbari2021", "Revisão sistemática; mostra foco em previsão e otimização, pouca detecção de risco."),
        ("wang2016", "Classificação descritivo, preditivo, prescritivo; ajuda a posicionar o projeto."),
        ("nguyen2018", "Revisão de big data analytics em cadeia de suprimentos."),
        ("baryannis2019", "IA em risco de cadeia de suprimentos; risco ali é ruptura, não acidente."),
    ]),
    ("Pátios, docas, centros de distribuição e portos", [
        ("vanderspoel2017", "ML com dado real de um centro de distribuição (chegada de caminhões)."),
        ("benjatanont2020", "MIT: previsão de tempo de permanência de caminhões num operador logístico nos EUA."),
        ("dotoig2018", "Liga tempo de permanência na instalação a risco de acidente (+6,2% por 15 min)."),
        ("chhetri2026", "ML para tempo de permanência de contêiner em pátio portuário."),
        ("gue1999", "Pesquisa operacional clássica de doca e layout de terminal."),
        ("boysen2010", "Revisão de agendamento de caminhões em cross-docks."),
        ("vanbelle2012", "Estado da arte de cross-docking."),
        ("huynh2016", "Revisão de sistemas de agendamento de caminhões em terminais."),
    ]),
    ("Telemetria e risco em caminhões", [
        ("driessen2024", "Frenagens bruscas por hora preveem sinistros com dano e multas."),
        ("cai2022", "Processos pontuais hierárquicos para eventos críticos recorrentes."),
        ("mehdizadeh2020", "Revisão de análise de dados em segurança viária."),
        ("guo2013", "Risco individual de motorista com dados de condução naturalística."),
        ("nas2017", "Debate sobre indicadores de segurança de transportadoras e exposição."),
    ]),
    ("Modelos estatísticos do projeto", [
        ("cameron2013", "Livro-texto de modelos de contagem."),
        ("mannering2014", "Fronteira metodológica em pesquisa de acidentes."),
        ("gelman2007", "Modelos hierárquicos e encolhimento."),
        ("clayton1987", "Bayes empírico para taxas de unidades pequenas."),
        ("hauer1997", "Bayes empírico em segurança viária; regressão à média."),
        ("spiegelhalter2005", "Gráficos de funil para comparar unidades de tamanhos diferentes."),
        ("lambert1992", "Poisson inflacionada de zeros."),
        ("dunn1996", "Resíduos quantílicos aleatorizados para diagnóstico."),
        ("brooks2017", "glmmTMB (R) para modelos mistos de contagem."),
        ("burkner2017", "brms (R) para modelos bayesianos hierárquicos."),
        ("fellegi1969", "Ligação probabilística de registros."),
    ]),
    ("Segurança ocupacional e fatores de risco", [
        ("sarkar2020", "Revisão de ML em análise de acidentes de trabalho."),
        ("collins1999", "Estudo clássico de lesões com empilhadeiras e veículos industriais."),
        ("wali2022", "Investigação de morte: motorista atropelado por caminhão de pátio."),
        ("dembe2005", "Hora extra e jornada longa aumentam o risco: covariável candidata."),
        ("breslin2006", "Recém-contratados têm risco muito maior: covariável candidata."),
        ("smith2010", "Temporários de agência têm taxa de lesão maior."),
    ]),
    ("Subnotificação", [
        ("leigh2004", "Estimativa nacional de lesões não contadas nos EUA."),
        ("boden2008", "Captura e recaptura em seis estados; subnotificação varia muito."),
        ("iwgdmf1995", "Teoria de captura e recaptura com múltiplas fontes."),
    ]),
    ("Dados públicos", [
        ("yogape2025", "Dataset do Kaggle usado no estudo preliminar (estrutura de exposição; incidentes aleatórios)."),
    ]),
    ("Previsão (extensão opcional)", [
        ("hyndman2021", "Livro aberto de previsão de séries temporais."),
        ("gneiting2007", "Regras de pontuação próprias (CRPS, perda quantílica)."),
    ]),
]


def ler_bib(caminho: Path) -> dict:
    texto = caminho.read_text(encoding="utf-8")
    entradas = {}
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)\n\}", texto, re.S):
        campos = dict(re.findall(r"(\w+)\s*=\s*\{(.*?)\},?\s*\n", m.group(3) + "\n", re.S))
        entradas[m.group(2).strip()] = {k.lower(): " ".join(v.split()) for k, v in campos.items()}
    return entradas


def link(e: dict) -> str:
    if "doi" in e:
        return f"\\href{{https://doi.org/{e['doi']}}}{{abrir pelo DOI}}"
    if "url" in e:
        return f"\\href{{{e['url']}}}{{abrir o link}}"
    titulo = re.sub(r"[{}\\]", "", e.get("title", ""))
    q = urllib.parse.quote_plus(titulo).replace("%", "\\%")
    return f"\\href{{https://scholar.google.com/scholar?q={q}}}{{buscar no Google Scholar}}"


def main() -> None:
    bib = ler_bib(BIB)
    usadas = set()
    linhas = []
    for titulo, itens in TEMAS:
        linhas.append(f"\\section{{{titulo}}}\n\\begin{{enumerate}}[leftmargin=*]")
        for chave, motivo in itens:
            if chave not in bib:
                raise KeyError(f"{chave} nao esta no referencias.bib")
            usadas.add(chave)
            motivo = motivo.replace("%", "\\%")
            linhas.append(f"  \\item \\fullcite{{{chave}}}\\\\\n  \\textit{{Por que ler:}} {motivo}\\\\\n"
                          f"  {link(bib[chave])} \\hfill $\\square$ \\textsf{{\\small lido}}")
        linhas.append("\\end{enumerate}\n")
    resto = sorted(set(bib) - usadas)
    if resto:
        linhas.append("\\section{Sem tema}\n\\begin{enumerate}[leftmargin=*]")
        linhas += [f"  \\item \\fullcite{{{k}}} \\hfill {link(bib[k])}" for k in resto]
        linhas.append("\\end{enumerate}\n")
    (AQUI / "lista_corpo.tex").write_text("\n".join(linhas), encoding="utf-8")
    print(f"{len(usadas)} referencias em {len(TEMAS)} temas; {len(resto)} sem tema")


if __name__ == "__main__":
    main()
