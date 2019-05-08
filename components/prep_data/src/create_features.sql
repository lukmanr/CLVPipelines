SELECT
  tf.customer_id,
  -- For training period
  -- Copying the calculations from Lifetimes where first orders are ignored
  -- See https://github.com/CamDavidsonPilon/lifetimes/blob/master/lifetimes/utils.py#L246
--[START features_target]
  ROUND(tf.monetary, 2) as monetary,
  tf.cnt_orders AS frequency,
  tf.recency,
  tf.T,
  ROUND(tf.recency/cnt_orders, 2) AS time_between,
  ROUND(tf.avg_basket_value, 2) AS avg_basket_value,
  ROUND(tf.avg_basket_size, 2) AS avg_basket_size,
  tf.cnt_returns,
  -- Target calculated for overall period
  ROUND(tt.target_monetary, 2) as target_monetary
--[END features_target]
FROM
  -- This SELECT uses only data before threshold to make features.
  (
    SELECT
      customer_id,
      SUM(order_value) AS monetary,
      DATE_DIFF(MAX(order_date), MIN(order_date), DAY) AS recency,
      DATE_DIFF(DATE('<<threshold_date>>'), MIN(order_date), DAY) AS T,
      COUNT(DISTINCT order_date) AS cnt_orders,
      AVG(order_qty_articles) avg_basket_size,
      AVG(order_value) avg_basket_value,
      SUM(CASE
          WHEN order_value < 1 THEN 1
          ELSE 0 END) AS cnt_returns
    FROM
      -- Makes the order value = 0 if it is the first one
      (
        SELECT
          a.*,
          (CASE
              WHEN a.order_date = c.order_date_min THEN 0
              ELSE a.order_value END) AS order_value_btyd
        FROM
          `<<project_id>>.<<dataset_id>>.<<order_summaries_table_id>>` a
        INNER JOIN (
          SELECT
            customer_id,
            MIN(order_date) AS order_date_min
          FROM
            `<<project_id>>.<<dataset_id>>.<<order_summaries_table_id>>`
          GROUP BY
            customer_id) c
        ON
          c.customer_id = a.customer_id
      )
    WHERE
      order_date <= DATE('<<threshold_date>>')
    GROUP BY
      customer_id) tf,

  -- This SELECT uses all records to calculate the target (could also use data after threshold )
  (
    SELECT
      customer_id,
      SUM(order_value) target_monetary
    FROM
      `<<project_id>>.<<dataset_id>>.<<order_summaries_table_id>>`
      --WHERE order_date > DATE('<<threshold_date>>')
    GROUP BY
      customer_id) tt
WHERE
  tf.customer_id = tt.customer_id
  AND tf.monetary > 0
  AND tf.monetary <= <<max_monetary>>