-- Questão 5 - Dimensão de Calendário e Análise de Lojas Físicas (LH Nautical)

WITH RECURSIVE date_bounds AS (
    -- Step 1: Find min and max transaction dates for physical stores (POS)
    SELECT 
        MIN(placed_at::date) AS min_date,
        MAX(placed_at::date) AS max_date
    FROM orders
    WHERE channel = 'pos'
      AND status IN ('paid', 'confirmed')
),

calendar AS (
    -- Step 2: Generate a continuous date dimension covering every single day in the period
    SELECT 
        generate_series(
            (SELECT min_date FROM date_bounds),
            (SELECT max_date FROM date_bounds),
            interval '1 day'
        )::date AS calendar_date
),

daily_sales AS (
    -- Step 3: Aggregate actual daily revenue for physical stores (POS)
    SELECT 
        placed_at::date AS sale_date,
        SUM(total) AS daily_revenue
    FROM orders
    WHERE channel = 'pos'
      AND status IN ('paid', 'confirmed')
    GROUP BY placed_at::date
),

full_calendar_sales AS (
    -- Step 4: LEFT JOIN calendar with daily sales, filling missing days with 0
    SELECT 
        c.calendar_date,
        COALESCE(s.daily_revenue, 0) AS total_sales,
        EXTRACT(DOW FROM c.calendar_date) AS day_of_week_num,
        CASE EXTRACT(DOW FROM c.calendar_date)
            WHEN 0 THEN 'Domingo'
            WHEN 1 THEN 'Segunda-feira'
            WHEN 2 THEN 'Terça-feira'
            WHEN 3 THEN 'Quarta-feira'
            WHEN 4 THEN 'Quinta-feira'
            WHEN 5 THEN 'Sexta-feira'
            WHEN 6 THEN 'Sábado'
        END AS day_of_week_name
    FROM calendar c
    LEFT JOIN daily_sales s ON c.calendar_date = s.sale_date
)

-- Step 5: Calculate true average sales per day of the week including zero-sales days
SELECT 
    day_of_week_name AS dia_semana,
    COUNT(calendar_date) AS total_dias_no_periodo,
    ROUND(SUM(total_sales), 2) AS faturamento_total,
    ROUND(AVG(total_sales), 2) AS media_vendas_diaria
FROM full_calendar_sales
GROUP BY day_of_week_num, day_of_week_name
ORDER BY media_vendas_diaria ASC;