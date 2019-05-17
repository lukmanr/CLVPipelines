
# Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging

import pyspark
from pyspark.sql.types import *
from pyspark.sql.functions import *

def prepare_features(
    source_gcs_path,
    output_gcs_path,
    threshold_date,
    predict_end,
    max_monetary,
    max_partitions):
    """Creates CLV features from sales transactions"""

    sc = pyspark.SparkContext()
    spark = pyspark.sql.SparkSession(sc)
    spark.conf.set("spark.sql.shuffle.partitions", max_partitions)

    sparkSQL = pyspark.sql.SQLContext(sc)

    schema = StructType([
        StructField('invoice_id', StringType()),
        StructField('stock_code', StringType()),
        StructField('description', StringType()),
        StructField('quantity', IntegerType()),
        StructField('invoice_date', StringType()),
        StructField('unit_price', FloatType()),
        StructField('customer_id', StringType()),
        StructField('country', StringType())
    ])

    # Read source file and select columns that will be the base of training features
    sales_transactions = sparkSQL.read \
    .csv(source_gcs_path, header=None, schema=schema) \
    .select('customer_id', to_date(col('invoice_date'), 'MM/dd/yy').alias('order_date'), 'quantity','unit_price') 

    # Find the most recent order's date for each customer
    latest_orders = sales_transactions \
    .groupBy('customer_id') \
    .agg(max('order_date').alias('latest_order')) \
    .select('customer_id', 'latest_order')

    # Calculate daily summaries
    daily_summaries = sales_transactions \
    .groupBy('customer_id', 'order_date') \
    .agg(sum(col('quantity')*col('unit_price')).alias('order_value'), 
        sum(col('quantity')).alias('order_qty_articles')) \
    .withColumn('positive_value', when(col('order_value') > 0, 1).otherwise(0)) \
    .join(latest_orders, 'customer_id')

    # Find customers with more than one positive order before the threshold date
    customers_to_include = daily_summaries \
    .filter(col('order_date') < threshold_date) \
    .groupBy('customer_id').agg(sum(col('positive_value')).alias('count_positive_values')) \
    .filter(col('count_positive_values') > 1) \
    .select('customer_id')

    # Filter out customers with less then 2 positive orders before the threshold date
    # and customers with inconsistent returns
    filtered_daily_summaries = daily_summaries \
    .join(customers_to_include, 'customer_id') \
    .filter(datediff(to_date(lit(predict_end)), col('latest_order')) < 90) \
    .filter((col('order_qty_articles')*col('order_value'))>0)

    # Calculate a monetary target for each customer
    monetary_targets = filtered_daily_summaries \
    .filter(col('order_date')>threshold_date) \
    .groupBy('customer_id') \
    .agg(sum('order_value').alias('target_monetary')) \
    .select('customer_id', 'target_monetary')

    # Calculate features for each customer
    features = filtered_daily_summaries \
    .filter(col('order_date')<=threshold_date) \
    .groupBy('customer_id') \
    .agg(sum('order_value').alias('monetary'),
        avg('order_value').alias('avg_basket_value'),
        avg('order_qty_articles').alias('avg_basket_size'),
        datediff(max('order_date'), min('order_date')).alias('recency'),
        datediff(to_date(lit(threshold_date)), min('order_date')).alias('T'),
        countDistinct('order_date').alias('cnt_orders'),
        sum(when(col('order_value')<0, 1).otherwise(0)).alias('cnt_returns')) \
    .filter((col('monetary')>0) & (col('monetary')<max_monetary))

    # Join features with targets
    features_and_target = features \
    .join(monetary_targets, 'customer_id')

    # Write the output to GCS
    #features_and_target.coalesce(4).write.csv(output_folder, mode='overwrite')
    features_and_target.write.csv(output_gcs_path, mode='overwrite')

def _parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--source-gcs-path',
        type=str,
        required=True,
        help='The GCS location with sales transaction CSV files.')
    parser.add_argument(
        '--output-gcs-path',
        type=str,
        required=True,
        help='The GCS location for the output feature files')
    parser.add_argument(
        '--threshold-date',
        type=str,
        required=True,
        help='Begining date for target value calculations.')
    parser.add_argument(
        '--predict-end',
        type=str,
        required=True,
        help='End date for target value calculations.')
    parser.add_argument(
        '--max-monetary',
        type=str,
        default=15000,
        help='Maximum monetary value.') 
    parser.add_argument(
        '--max-partitions',
        type=int,
        default=8,
        help='Maximum number of partitions.') 
    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    args = _parse_arguments()

    prepare_features(
        source_gcs_path=args.source_gcs_path,
        output_gcs_path=args.output_gcs_path,
        threshold_date=args.threshold_date,
        predict_end=args.predict_end,
        max_monetary=args.max_monetary,
        max_partitions=args.max_partitions
    )
    

