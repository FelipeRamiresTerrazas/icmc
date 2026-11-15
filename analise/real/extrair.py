"""Extrai AGREGADOS dos dados reais para a exploracao de viabilidade (uso interno).

Somente leitura, pelo usuario de servico CLAUDE_CODE_SVC (chave em ~/.snowflake/).
Nenhum nome, ID de pessoa, texto livre, GPS ou midia: o menor grao salvo e
veiculo x mes (veiculo identificado so pelo ID interno da Samsara).
Saida em resultados/real/ (fora do git).

Uso (na raiz do repo):  .venv/Scripts/python.exe analise/real/extrair.py [consulta ...]
"""

import re
import sys
from pathlib import Path

import pandas as pd
import snowflake.connector

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "resultados" / "real"
INICIO, FIM = "2025-10-01", "2026-10-01"   # 12 meses completos com Samsara e YardSafe

NORM = "upper(regexp_replace(trim({c}), '[ -]', ''))"

BASE = f"""
with v as (
  select id as vehicle_id, {NORM.format(c='name')} as truck
  from RAW_FIVETRAN.SAMSARA.VEHICLE where not coalesce(_fivetran_deleted, false)),
tagfilha as (
  select tv.vehicle_id, c.name as tag, p.name as raiz
  from RAW_FIVETRAN.SAMSARA.TAG_VEHICLE tv
  join RAW_FIVETRAN.SAMSARA.TAGS c on c.id = tv.tag_id
  join RAW_FIVETRAN.SAMSARA.TAGS p on p.id = c.parent_tag_id
  where not coalesce(tv._fivetran_deleted, false)),
site as (
  select vehicle_id, min(regexp_substr(tag, '(SP|SH)[0-9]{{4}}')) as site, min(raiz) as regiao
  from tagfilha where raiz like '%Region' group by 1),
uso as (
  select vehicle_id, min(tag) as uso from tagfilha where raiz = 'Fleet Usage Type' group by 1),
rep as (
  select id, status, {NORM.format(c='truck_number')} as truck, nullif(trim(site_location_code), '') as site_rep,
         try_to_date(actual_incident_date) as d, insurance_claim
  from RAW.ACCIDENTS_INJURIES.INCIDENTS where incident_type = 'accident_incident')
"""

CONSULTAS = {
    # painel veiculo x mes: exposicao + acidentes (todas as definicoes)
    "painel": BASE + f"""
, trips as (
  select vehicle_id, date_trunc('month', to_timestamp_ntz(start_ms / 1000))::date as mes,
         sum(distance_meters) / 1609.344 as milhas, sum(end_ms - start_ms) / 3.6e6 as horas,
         count(*) as viagens, count(distinct to_date(to_timestamp_ntz(start_ms / 1000))) as dias
  from RAW_FIVETRAN.SAMSARA.VEHICLE_TRIP
  where not coalesce(_fivetran_deleted, false) and end_ms > start_ms and end_ms - start_ms <= 86400000
    and to_timestamp_ntz(start_ms / 1000) >= '{INICIO}' and to_timestamp_ntz(start_ms / 1000) < '{FIM}'
  group by 1, 2),
acc as (
  select v.vehicle_id, date_trunc('month', rep.d)::date as mes, count(*) as acid,
         count_if(rep.status = 'reviewed') as acid_rev, count_if(rep.insurance_claim = 'Yes') as acid_seguro
  from rep join v on v.truck = rep.truck group by 1, 2)
select t.*, coalesce(a.acid, 0) acid, coalesce(a.acid_rev, 0) acid_rev, coalesce(a.acid_seguro, 0) acid_seguro,
       s.site, s.regiao, u.uso
from trips t left join acc a on a.vehicle_id = t.vehicle_id and a.mes = t.mes
left join site s on s.vehicle_id = t.vehicle_id left join uso u on u.vehicle_id = t.vehicle_id
""",
    # eventos de telemetria por veiculo x mes x rotulo do sistema
    "eventos": f"""
select e.asset_id::text as vehicle_id, date_trunc('month', e.start_ms)::date as mes, l.label,
       count(*) as n_todos, count_if(e.event_state <> 'dismissed') as n_mantidos
from RAW_FIVETRAN.SAMSARA.SAFETY_EVENT e
join RAW_FIVETRAN.SAMSARA.SAFETY_EVENT_BEHAVIOR_LABEL l on l.safety_event_id = e.id and l.source = 'SYSTEM'
where not coalesce(e._fivetran_deleted, false) and e.start_ms >= '{INICIO}' and e.start_ms < '{FIM}'
group by 1, 2, 3
""",
    # funil de ligacao dos relatos de acidente (contagens por mes e status)
    "funil": BASE + """
select date_trunc('month', rep.d)::date as mes, rep.status,
       count(*) as relatos,
       count(rep.truck) - count_if(rep.truck = '') as com_caminhao,
       count(v.vehicle_id) as casa_samsara,
       count(s.site) as com_site_tag,
       count(rep.site_rep) as com_site_relato,
       count_if(rep.site_rep = s.site) as site_concorda
from rep left join v on v.truck = rep.truck left join site s on s.vehicle_id = v.vehicle_id
group by 1, 2
""",
    # colisoes detectadas x relatadas (+-2 dias, mesmo veiculo), por site
    "colisoes": BASE + f"""
, crash as (
  select distinct e.id, e.asset_id::text as vehicle_id, to_date(e.start_ms) as d,
         iff(e.event_state = 'dismissed', 'descartada', 'mantida') as estado
  from RAW_FIVETRAN.SAMSARA.SAFETY_EVENT e
  join RAW_FIVETRAN.SAMSARA.SAFETY_EVENT_BEHAVIOR_LABEL l on l.safety_event_id = e.id and l.label = 'Crash'
  where not coalesce(e._fivetran_deleted, false) and e.start_ms >= '{INICIO}' and e.start_ms < '2026-10-14'),
r as (select rep.id, v.vehicle_id, rep.d from rep join v on v.truck = rep.truck
      where rep.d >= '{INICIO}' and rep.d < '2026-10-14'),
c2 as (select c.id, c.vehicle_id, c.estado, max(iff(r.id is not null, 1, 0)) as casou
       from crash c left join r on r.vehicle_id = c.vehicle_id and abs(datediff('day', c.d, r.d)) <= 2
       group by 1, 2, 3),
r2 as (select r.id, r.vehicle_id,
              max(iff(c.id is not null and c.estado = 'mantida', 1, 0)) as tem_mantida,
              max(iff(c.id is not null, 1, 0)) as tem_qualquer
       from r left join crash c on c.vehicle_id = r.vehicle_id and abs(datediff('day', c.d, r.d)) <= 2
       group by 1, 2)
select 'deteccao' as lado, s.site, u.uso, c2.estado as grupo, c2.casou as casou, count(*) as n
from c2 left join site s on s.vehicle_id = c2.vehicle_id left join uso u on u.vehicle_id = c2.vehicle_id
group by 1, 2, 3, 4, 5
union all
select 'relato', s.site, u.uso, iff(r2.tem_mantida = 1, 'com_mantida', iff(r2.tem_qualquer = 1, 'so_descartada', 'sem')), null, count(*)
from r2 left join site s on s.vehicle_id = r2.vehicle_id left join uso u on u.vehicle_id = r2.vehicle_id
group by 1, 2, 3, 4, 5
""",
    # horas ADP por semana e departamento
    "adp": """
select week_start, timecard_work_department as site, pay_code_category, sum(hours) as horas
from ANALYTICS_DB.MARTS.FACT_TIMECARD_SUPERVISOR_PAY_CODE
where week_start is not null group by 1, 2, 3
""",
    # capitulo descritivo: relatos por hora, dia da semana, tipo e status (sem texto livre)
    "horario": """
select hour(try_to_time(actual_incident_time)) as hora,
       dayofweekiso(try_to_date(actual_incident_date)) as dia_semana,
       date_trunc('month', try_to_date(actual_incident_date))::date as mes,
       incident_type, truck_type, status,
       iff(status = 'pending' and try_to_date(submitted_at) between '2026-05-01' and '2026-10-31', 1, 0) as suspeito_teste,
       count(*) as n
from RAW.ACCIDENTS_INJURIES.INCIDENTS group by 1, 2, 3, 4, 5, 6, 7
""",
    # capitulo descritivo: categorias fechadas de causa (nenhum campo de texto livre)
    "causas": """
select incident_type, truck_type, accident_root_cause, work_injury_root_cause, status,
       date_trunc('month', try_to_date(actual_incident_date))::date as mes, count(*) as n
from RAW.ACCIDENTS_INJURIES.INCIDENTS group by 1, 2, 3, 4, 5, 6
""",
    # ordens de manutencao por dano, por mes (motivo com TRIM; grafia com espacos marca o regime antigo)
    "manutencao": """
select date_trunc('month', opened_date)::date as mes, trim(repreason) as motivo,
       iff(repreason <> trim(repreason), 1, 0) as com_espacos, count(distinct orderid) as ordens
from EDW_PROD_100460.EDW_PROD_100460.FCT_AMORDERSEC
where trim(repreason) in ('DAMAGE', 'ACC-REPORTED') group by 1, 2, 3
""",
    # auditorias de seguranca por site: uma linha por avaliacao, site so como hash, sem nomes de auditores
    "auditorias": """
select date_trunc('month', "AssessmentDate")::date as mes, "AssessmentType" as tipo, "Status" as status,
       md5("Site") as site_h, "ScorePercent" as pct, "TotalPointsEarned" as pontos, "TotalPointsPossible" as pontos_max
from DOMOVIEW."cust_mmmm_0034_2137".ACCIDENTS_INJURIES_POWER_APPS_RAW
""",
    # cobertura dos relatos por mes do incidente e status (todos os tipos)
    "relatos": """
select date_trunc('month', try_to_date(actual_incident_date))::date as mes, status, incident_type,
       count(*) as n, count(nullif(trim(truck_number), '')) as com_caminhao,
       count(nullif(trim(site_location_code), '')) as com_site
from RAW.ACCIDENTS_INJURIES.INCIDENTS group by 1, 2, 3
""",
}


def conectar():
    cfg = (Path.home() / ".snowflake" / "claude_sf.py").read_text(encoding="utf-8")
    conta = re.search(r'account="([^"]+)"', cfg).group(1)
    return snowflake.connector.connect(
        account=conta, user="CLAUDE_CODE_SVC", authenticator="SNOWFLAKE_JWT",
        private_key_file=str(Path.home() / ".snowflake" / "keys" / "claude_svc_key.p8"),
        role="CLAUDE_READONLY", warehouse="ANALYTICS_WH", login_timeout=30)


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    conn = conectar()
    try:
        nomes = sys.argv[1:] or list(CONSULTAS)
        for nome in nomes:
            sql = CONSULTAS[nome]
            cur = conn.cursor()
            cur.execute(sql)
            df = pd.DataFrame(cur.fetchall(), columns=[d[0].lower() for d in cur.description])
            df.to_csv(SAIDA / f"{nome}.csv.gz", index=False)
            print(f"{nome}: {len(df)} linhas")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
