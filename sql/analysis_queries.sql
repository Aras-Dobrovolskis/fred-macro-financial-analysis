-- 1. Preview the full merged monthly dataset
SELECT date,
       cpi,
       fedfunds,
       sp500,
       vix,
       sp500_pct_change,
       inflation_pct_change,
       rate_regime,
       volatility_regime
FROM fred_monthly_data
ORDER BY date;

-- 2. Filter a date range for the most recent 24 months
SELECT *
FROM fred_monthly_data
WHERE date >= '2024-01-31'
ORDER BY date;

-- 3. Average S&P 500 monthly return by year
SELECT strftime('%Y', date) AS year,
       ROUND(AVG(sp500_pct_change), 6) AS avg_sp500_return
FROM fred_monthly_data
GROUP BY year
ORDER BY year;

-- 4. Average S&P 500 return by rising/falling/flat rate regimes
SELECT rate_regime,
       COUNT(*) AS months,
       ROUND(AVG(sp500_pct_change), 6) AS avg_sp500_return
FROM fred_monthly_data
GROUP BY rate_regime
ORDER BY months DESC;

-- 5. Inflation and stock-market return comparison
SELECT date,
       inflation_pct_change,
       sp500_pct_change
FROM fred_monthly_data
ORDER BY date DESC
LIMIT 20;

-- 6. VIX regime return analysis
SELECT volatility_regime,
       COUNT(*) AS months,
       ROUND(AVG(sp500_pct_change), 6) AS avg_sp500_return,
       ROUND(AVG(vix), 4) AS avg_vix
FROM fred_monthly_data
GROUP BY volatility_regime
ORDER BY avg_vix DESC;

-- 7. Average returns by combined rate and volatility regime
SELECT rate_regime,
       volatility_regime,
       COUNT(*) AS months,
       ROUND(AVG(sp500_pct_change), 6) AS avg_sp500_return
FROM fred_monthly_data
GROUP BY rate_regime, volatility_regime
ORDER BY rate_regime, volatility_regime;
