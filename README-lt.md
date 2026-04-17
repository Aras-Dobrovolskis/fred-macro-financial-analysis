# Finansų projektas: FRED makro-finansinė analizė

[English version](README.md)

## Projekto apžvalga
Šis projektas sukuria mėnesinį makro-finansinį duomenų rinkinį iš FRED duomenų, išsaugo jį SQLite duomenų bazėje ir analizuoja, kaip S&P 500 grąža siejasi su palūkanų normomis, infliacija ir rinkos volatilumu.

### Verslo tikslas
Investuotojams ir finansų analitikams svarbu palyginti akcijų rinką, palūkanų normas, infliaciją ir volatilumą vienu laiko intervalu. Šis projektas padeda suprasti, kaip S&P 500 elgiasi skirtinguose palūkanų, infliacijos ir rizikos režimuose.

## Duomenų aprašymas
Projekte naudojami FRED CSV failai kataloge `data/`:
- `sp500.csv` — dienos S&P 500 uždarymo kainos
- `fedfunds.csv` — mėnesinė federalinių fondų palūkanų norma
- `cpi.csv` — mėnesio vartotojų kainų indekso (CPI) reikšmės
- `vix.csv` — dienos VIX rizikos indekso uždarymo kainos

Dienos serijos yra konvertuojamos į mėnesines vertes pagal paskutinį mėnesio prekybos dienos uždarymą.

Duomenų šaltinis: Federal Reserve Economic Data (FRED).

## Naudoti įrankiai
- Python 3
- pandas
- sqlite3
- matplotlib
- standartinės Python bibliotekos (`pathlib`)

## Projekto struktūra
```
project_root/
├── data/
│   ├── cpi.csv
│   ├── fedfunds.csv
│   ├── sp500.csv
│   └── vix.csv
├── output/
│   ├── fred_monthly_merged.csv
│   ├── finance_project.db
│   └── charts/
├── sql/
│   └── analysis_queries.sql
├── notebooks/
│   └── finance_analysis.ipynb
├── src/
│   ├── data_cleaning.py
│   ├── database_build.py
│   └── analysis.py
├── .gitignore
├── LICENSE
├── README.md
├── README-lt.md
└── requirements.txt
```

## Ką daro projektas
- nuskaityti originalius FRED CSV failus
- suvienodinti stulpelių pavadinimus ir datos formatą
- dienos serijas (`sp500`, `vix`) agreguoti iki mėnesinių reikšmių naudojant paskutinę prekybos dienos uždarymo vertę
- mėnesines serijas (`cpi`, `fedfunds`) suderinti pagal mėnesio pabaigą
- sujungti duomenis į vieną mėnesinį rinkinį
- sukurti papildomus analitinius skaičiavimo laukus:
  - `sp500_pct_change`
  - `inflation_pct_change`
  - `rate_change`
  - `rate_regime`
  - `volatility_regime`

Procentinio pokyčio stulpeliai saugomi dešimtainiu formatu, kur `0.01` reiškia `1%`.
VIX režimai yra paprastos analitinės kategorijos: `low` yra mažiau nei 18, `medium` yra nuo 18 iki mažiau nei 25, o `high` yra 25 arba daugiau.

## Išvalymo santrauka
Skriptas `src/data_cleaning.py`:
- užtikrina, kad visi keturi įvesties failai egzistuoja
- konvertuoja `observation_date` į `date`
- veda visus skaičius į `float` ir išvalo `NaN`
- dienos serijas sukonvertuoja į mėnesio pabaigos reikšmes
- sujungia visas keturias serijas ir pašalina mėnesius, kuriuose trūksta duomenų
- išsaugo rezultatą kaip `output/fred_monthly_merged.csv`

## SQL analizė
Failas `sql/analysis_queries.sql` apima naudingas analizės užklausas:
- pilno duomenų rinkinio peržiūra
- filtravimas pagal laikotarpį
- metiniai vidutiniai S&P 500 grąžos rodikliai
- vidutinė S&P 500 grąža skirtinguose palūkanų normų režimuose
- infliacijos ir rinkos grąžos palyginimas
- VIX režimų analizė
- kombinacinė palūkanų ir volatilumo režimų grąža

## Svarbiausios įžvalgos
- duomenų rinkinys aprėpia 2021-04-30 iki 2026-03-31 ir turi 60 mėnesinių įrašų.
- daugiausia metų S&P 500 mėnesinė grąža yra teigiama, o 2022 ir 2026 metai yra vidutiniškai neigiami.
- kylant palūkanų normoms, S&P 500 vidutinė mėnesinė grąža yra mažesnė (~0.52%) nei krintant arba esant fiksuotai palūkanų normai (~0.99% ir ~1.04%).
- žemos volatilumo mėnesiai duoda didžiausią vidutinę grąžą (~2.32%), o aukštos volatilumo mėnesiai — neigiamą vidutinę grąžą (~-3.54%).

## Diagramų peržiūra
![S&P 500 mėnesio uždarymo vertė](output/charts/sp500_over_time.png)
![Vidutinė S&P 500 grąža pagal palūkanų režimą](output/charts/avg_return_by_rate_regime.png)
![Vidutinė S&P 500 grąža pagal volatilumo režimą](output/charts/avg_return_by_volatility_regime.png)

## Ką rodo diagramos
- `sp500_over_time.png` rodo S&P 500 kainos tendenciją per mėnesius.
- `fedfunds_over_time.png` rodo federalinių fondų palūkanų kreivę per laikotarpį.
- `cpi_over_time.png` rodo infliacijos slinkimą pagal CPI.
- `vix_over_time.png` parodo volatilumo režimus ir VIX šuolius.
- `sp500_vs_fedfunds.png` parodo S&P 500 grąžą priklausomai nuo palūkanų normos lygio.
- `sp500_vs_inflation.png` rodo S&P 500 grąžos ir infliacijos santykį.
- `avg_return_by_rate_regime.png` rodo vidutinę grąžą skirtinguose palūkanų režimuose.
- `avg_return_by_volatility_regime.png` parodo vidutinę grąžą skirtinguose volatilumo režimuose.

## Kaip paleisti projektą
1. Įdiekite priklausomybes:
```bash
python -m pip install -r requirements.txt
```
2. Sukurkite išvalytą mėnesinį duomenų rinkinį:
```bash
python src/data_cleaning.py
```
3. Sukurkite SQLite duomenų bazę:
```bash
python src/database_build.py
```
4. Paleiskite analizę ir sugeneruokite diagramas:
```bash
python src/analysis.py
```
5. Atidarykite `notebooks/finance_analysis.ipynb` interaktyviai peržiūrai.

## Ateities patobulinimai
- pridėti portfelio rizikos ir grąžos palyginimą su drawdown metrikomis
- įtraukti papildomus makro rodiklius, pavyzdžiui, nedarbo lygį ar BVP augimą
- papildyti analizę dividendais koreguota S&P 500 grąža
- sukurti automatizuotą režimų pagrindu veikiančią investavimo strategiją
