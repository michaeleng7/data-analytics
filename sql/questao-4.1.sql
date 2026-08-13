SELECT 
    co.customer_id,
    co.faturamento_total,
    co.frequencia,
    (co.faturamento_total / co.frequencia) AS ticket_medio,
    cc.diversidade_categorias
FROM (
    SELECT 
        customer_id,
        SUM(total) AS faturamento_total,
        COUNT(id) AS frequencia
    FROM orders
    GROUP BY customer_id
) co
JOIN (
    SELECT 
        o.customer_id,
        COUNT(DISTINCT p.category_id) AS diversidade_categorias
    FROM orders o
    JOIN order_items oi ON o.id = oi.order_id
    JOIN product_variants pv ON oi.product_variant_id = pv.id
    JOIN products p ON pv.product_id = p.id
    GROUP BY o.customer_id
) cc ON co.customer_id = cc.customer_id
WHERE cc.diversidade_categorias >= 13
ORDER BY ticket_medio DESC, co.customer_id ASC
LIMIT 10;