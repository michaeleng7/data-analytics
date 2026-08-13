-- Questão 4 - Análise de Clientes de Elite (LH Nautical)

WITH client_category_stats AS (
    -- Step 1: Calculate Total Revenue, Order Frequency, Ticket Médio, and Distinct Categories per Customer
    SELECT 
        o.customer_id,
        SUM(o.total) AS total_revenue,
        COUNT(DISTINCT o.id) AS total_orders,
        (SUM(o.total) / COUNT(DISTINCT o.id)) AS avg_ticket,
        COUNT(DISTINCT p.category_id) AS distinct_categories_count
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    JOIN product_variants pv ON oi.product_variant_id = pv.id
    JOIN products p ON pv.product_id = p.id
    WHERE o.status IN ('paid', 'confirmed')
    GROUP BY o.customer_id
    HAVING COUNT(DISTINCT p.category_id) >= 13
),

top_10_elite_clients AS (
    -- Step 2: Filter top 10 clients with highest Ticket Médio (Tie-breaker: customer_id ASC)
    SELECT 
        customer_id,
        total_revenue,
        total_orders,
        avg_ticket,
        distinct_categories_count
    FROM client_category_stats
    ORDER BY avg_ticket DESC, customer_id ASC
    LIMIT 10
)

-- Step 3: Identify the top purchased product category by total quantity for these 10 elite clients
SELECT 
    c.id AS category_id,
    c.name AS category_name,
    SUM(oi.quantity) AS total_items_purchased
FROM top_10_elite_clients e
JOIN orders o ON e.customer_id = o.customer_id
JOIN order_items oi ON o.id = oi.order_id
JOIN product_variants pv ON oi.product_variant_id = pv.id
JOIN products p ON pv.product_id = p.id
JOIN categories c ON p.category_id = c.id
WHERE o.status IN ('paid', 'confirmed')
GROUP BY c.id, c.name
ORDER BY total_items_purchased DESC
LIMIT 1;