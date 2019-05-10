SELECT
  a.customer_id,
  a.order_date,
  a.order_value,
  a.order_qty_articles
FROM
(
  SELECT
    customer_id,
    order_date,
    ROUND(SUM(unit_price * quantity), 2) AS order_value,
    SUM(quantity) AS order_qty_articles,
    (
      SELECT
        MAX(order_date)
      FROM
        `{{transactions_table_fqn}}` tl
      WHERE
        tl.customer_id = t.customer_id
    ) latest_order
  FROM
    `{{transactions_table_fqn}}` t
  GROUP BY
      customer_id,
      order_date
) a

INNER JOIN (
  -- Only customers with more than one positive order values before threshold.
  SELECT
    customer_id
  FROM (
    -- Customers and how many positive order values  before threshold.
    SELECT
      customer_id,
      SUM(positive_value) cnt_positive_value
    FROM (
      -- Customer with whether order was positive or not at each date.
      SELECT
        customer_id,
        (
          CASE
            WHEN SUM(unit_price * quantity) > 0 THEN 1
            ELSE 0
          END ) positive_value
      FROM
        `{{transactions_table_fqn}}`
      WHERE
        order_date < DATE("{{threshold_date}}")
      GROUP BY
        customer_id,
        order_date)
    GROUP BY
      customer_id )
  WHERE
    cnt_positive_value > 1
  ) b
ON
  a.customer_id = b.customer_id
--[START common_clean]
WHERE
  -- Bought in the past 3 months
  DATE_DIFF(DATE("{{predict_end}}"), latest_order, DAY) <= 90
  -- Make sure returns are consistent.
  AND (
    (order_qty_articles > 0 and order_Value > 0) OR
    (order_qty_articles < 0 and order_Value < 0)
  )