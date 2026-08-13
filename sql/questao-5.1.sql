-- Questão 5.1 - Calendar Dimension & POS Sales Analysis (LH Nautical)

SELECT 
    fcs.dia_semana,
    COUNT(fcs.calendar_date) AS total_dias_no_periodo,
    ROUND(SUM(fcs.total_sales)::numeric, 2) AS faturamento_total,
    ROUND(AVG(fcs.total_sales)::numeric, 2) AS media_vendas_diaria
FROM (
    -- Step 2: LEFT JOIN calendar dimension with daily sales, imputing 0 for missing days
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
        END AS dia_semana
    FROM (
        -- Step 1: Generate continuous date series between min and max POS sales dates
        SELECT 
            generate_series(
                MIN(placed_at::date),
                MAX(placed_at::date),
                INTERVAL '1 day'
            )::date AS calendar_date
        FROM orders
        WHERE channel = 'pos'
    ) c
    LEFT JOIN (
        -- Daily sales aggregation for physical stores (POS)
        SELECT 
            placed_at::date AS sale_date,
            SUM(total) AS daily_revenue
        FROM orders
        WHERE channel = 'pos'
        GROUP BY placed_at::date
    ) s ON c.calendar_date = s.sale_date
) fcs
GROUP BY fcs.day_of_week_num, fcs.dia_semana
ORDER BY media_vendas_diaria ASC;