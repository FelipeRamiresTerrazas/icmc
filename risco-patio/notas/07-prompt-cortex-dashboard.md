# 07. Prompt para o Cortex: dashboard exploratório em Streamlit

Nota **interna**: cita tabelas e sistemas da empresa (mesmo cuidado de `01` a `03`). Criada em 2026-11-11.

Uso: colar o bloco abaixo no Cortex Code (Snowsight). Antes, trocar `<APP_DB>.<APP_SCHEMA>` pelo schema pessoal ou de sandbox onde o app pode ser criado. Os nomes de tabela vêm do inventário (`01-inventario-dados.md`); nomes de coluna não foram todos conferidos, por isso o prompt manda o Cortex inspecionar antes.

```text
Build a Streamlit in Snowflake app named THESIS_RISK_EXPLORER in <APP_DB>.<APP_SCHEMA>.

## Purpose
I am preparing a master's research project on accident risk in yard truck operations (spotter, shuttle and OTR trucks). The unit of analysis is truck x month (fallback: site x month). The models will be hierarchical count models (negative binomial with an exposure offset and a truck random effect). The app is for exploring the data we have and deciding whether the design is feasible. It must answer:
- H1: are exposure-adjusted accident rates by site stable over time, and do they predict the next period better than raw counts?
- H2: do telematics behavior rates (harsh braking, harsh turns, following distance, speeding, phone use, etc.) predict accidents beyond exposure?
- H3: does underreporting vary by site (collisions detected by telematics vs accidents reported)?
- Extension: can weekly exposure (hours) be forecast for staffing and supervision planning?

## Hard rules (do not break any of these)
1. READ ONLY. Only SELECT statements on existing objects. Never CREATE, INSERT, UPDATE, DELETE, MERGE, ALTER or DROP anything, except creating the Streamlit app itself in <APP_DB>.<APP_SCHEMA>. No new tables or views; use CTEs.
2. NO PERSONAL DATA in the app or in any query result: never select or display person names, birth dates, race, sex, hire dates, employee or driver IDs, free-text fields (descriptions, why_1..why_5, statements, concerns), GPS coordinates, addresses, or camera media. IDs may be used only inside aggregates (e.g. COUNT(DISTINCT ...)).
3. Aggregate in SQL. Never pull raw rows into pandas; every query returns aggregated rows. Cache with st.cache_data(ttl=3600).
4. Never query RAW_FIVETRAN.SAMSARA.READING_HISTORY_FEED or RAW_FIVETRAN.SAMSARA.GPS (billions of rows).
5. Do not guess column names. First inspect every table below with DESCRIBE TABLE or INFORMATION_SCHEMA.COLUMNS and show me the list of tables, columns you will use and your assumptions (units, date columns, status values) BEFORE writing the app. If something I describe does not exist, tell me and skip that chart; do not invent a substitute silently.
6. Sites are anonymized by default: a sidebar toggle "Show real site codes" (default OFF) maps sites to "Site 01", "Site 02"... ordered by total exposure. Same idea for trucks: never show truck codes unless the toggle is on.
7. In tables, show counts below 5 as "<5" when anonymization is on.

## Data sources (verify names and columns first)
- Accident reports (YardSafe app, from Sep 2025): RAW.ACCIDENTS_INJURIES.INCIDENTS. Expected columns include actual_incident_date, incident_type (accident_incident, work_injury, other), other_category (Near Miss, ...), truck_type (D1 Spotter, D2 Shuttle, D3 OTR), truck_number, accident_root_cause, insurance_claim, site_location_code (ADP department code), submitted_at and a status column. About 130 records with status "pending" between May and Oct 2026 look like tests: add a sidebar checkbox "Exclude suspected test records" (default ON) if a status column exists, and tell me which rule you used.
- Legacy reports (MS Forms, until Mar 2026, free-text site): RAW.ACCIDENTS_INJURIES.SAFETY_INCIDENT_REPORTING_LOAD. Use only to compare monthly counts with INCIDENTS.
- Site reference: RAW.ACCIDENTS_INJURIES.DIM_SITES_TREATED, and DIM_DEPARTMENT / DIM_SITE in the analytics marts (find the schema in ANALYTICS_DB).
- Telematics (Samsara via Fivetran, RAW_FIVETRAN.SAMSARA). The sync is frozen since 2026-10-13: draw a vertical marker at that date on every time chart and default the date filter to end there.
  - VEHICLE: NAME is the truck code (same pattern as truck_number, e.g. two letters + five digits).
  - VEHICLE_TRIP: trips with start, end and distance (exposure). Filter out trips with null end, end <= start, or duration > 24 h (about 0.3% are invalid and inflate hours). Check whether distance is in meters or miles and convert to miles.
  - SAFETY_EVENT and SAFETY_EVENT_BEHAVIOR_LABEL: event per vehicle with time, max g-force, speed, behavior label and review state (some events are dismissed by human review as false positives; find the column that says so).
  - TAGS and TAG_VEHICLE: child tags under the four region roots (Midwest, North East, South East, West) contain the ADP department code (format like SP1234 or SH1234) and therefore identify the truck's site. Other tag roots give truck usage (spot, local, shuttle), fuel (diesel, EV) and ownership (leased). Extract the code with a regex.
- Workforce hours (ADP): ANALYTICS_DB marts table FACT_TIMECARD_SUPERVISOR_PAY_CODE (hours by department, from Jun 2025). Exclude rows without a valid date.
- Yard moves (Yard Commander): FACT_MOVES_DROPOFF_COMPLETE (moves by campus and day). Campus names have no department code and no bridge exists yet, so show moves separately and do not join them to sites.

Truck matching rule: normalize both sides with UPPER, TRIM and removal of spaces and hyphens, then match INCIDENTS.truck_number to VEHICLE.NAME. Expected match rate is around 70% before normalization.

## Pages (use st.navigation or tabs)
Each page opens with one or two sentences on why it matters for the research and ends with an expander "Data caveats".

1. Coverage and quality
   - Monthly row counts per source on one timeline, with min and max dates per source.
   - Completeness of INCIDENTS fields by month (% non-null: site_location_code, truck_number, incident time, root cause, insurance_claim).
   - Monthly count comparison INCIDENTS vs legacy MS Forms where they overlap.
2. Linkage funnel
   - Accident reports -> with truck number -> truck matches a Samsara vehicle -> vehicle has a site tag -> site code exists in DIM_DEPARTMENT. Counts and % at each step, overall and by month.
   - Agreement between the report's site_location_code and the truck's tag site (share of matches per site).
   - Unmatched truck numbers summarized by pattern only (letters -> A, digits -> 9), with counts.
3. Exposure
   - Truck-month panel: miles, trip hours and active days per truck per month. Histograms, fleet size over time, split by usage tag and region.
   - Site-month: Samsara trip hours vs ADP hours (scatter, log scale) to check whether the two exposure measures agree.
4. Outcomes and the truck-month panel
   - Build the panel with all trucks that have trips in the month (zeros included), left join accidents matched by truck and month.
   - KPI row: number of truck-months, accidents matched to exposure, share of zero months, mean, variance and variance/mean ratio (overdispersion).
   - Distribution of accidents per truck-month; breakdown by truck_type and root cause.
   - Sidebar selector "Outcome definition": all reported accidents (default) vs accidents with insurance_claim = true. Show both totals side by side, because a preliminary simulation suggests about 300 accidents are needed for 0.75 power to detect a 0.3 log-rate effect per SD of a covariate.
5. Site rates and funnel plot (H1)
   - Accidents per 10,000 miles and per 1,000 ADP hours by site for the selected period.
   - Funnel plot: rate vs exposure with 95% and 99.8% Poisson control limits around the pooled rate.
   - Empirical Bayes rate (gamma-Poisson, method of moments) with 90% interval, next to the raw rate.
   - Rank stability: split the period in two halves and show the Spearman correlation between halves for raw counts, raw rates and empirical Bayes rates.
6. Telematics vs accidents (H2)
   - Per truck-month, rate per 1,000 miles of each behavior label (top 8 labels, rest as "Other"), computed two ways: all system events and only events not dismissed in review. Show the dismissed share per label.
   - For each label: binned plot (deciles of the rate in month t vs accidents per 10,000 miles in month t and in month t+1) and Spearman correlations.
7. Detected collisions vs reports (H3)
   - Samsara collision events not dismissed in review, matched to accident reports for the same truck within +/- 2 days.
   - Per site: detected (n1), reported (n2), both (m), reporting ratio m/n1, and Lincoln-Petersen estimate N = n1*n2/m with the Chapman correction and an approximate 95% interval. Show a warning when m < 5.
8. Exposure forecast (extension)
   - Weekly ADP hours, total and by site (selectable).
   - Compare on the last 8 weeks: mean of the previous 8 weeks, seasonal naive and simple exponential smoothing (statsmodels ETS if available in the Snowflake Anaconda channel, otherwise implement in numpy). Report MAPE and an 80% interval for the next 8 weeks.

## Sidebar filters
Date range, region, truck usage tag, outcome definition, exclude suspected tests, show real site codes.

## Style
Altair charts. White background. Colors: navy #153084 for structure and headers, royal blue #4269E2 as the main series and accent, ink #1B243A for text. Categorical order: #4269E2, #153084, #8EA6EE, #7F7F7F, #C9D3F5. Gridlines #D9D9D9, annotations #5F6470. Use red #C8423B and green #2E8B57 only when the data means bad or good (e.g. points outside the funnel limits).
Download buttons only for aggregated tables (CSV).

## Deliverable
Step 1: the inventory of tables and columns you found, the assumptions, and any question for me. Wait for my OK.
Step 2: the full app code (single streamlit_app.py plus environment.yml with the packages), with SQL in clearly named functions, and a short README of what each page computes.
```
