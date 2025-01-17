from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
from pyspark.sql.functions import col, to_date, avg, format_number, date_format, lag, when
from pyspark.sql.window import Window

spark = SparkSession.builder.appName("COVID_USD_Monthly_Percent_Change").getOrCreate()
spark.sparkContext.setLogLevel("ERROR") # Minimize console output

schema = StructType([
    StructField("date", StringType(), True),
    StructField("currency", StringType(), True),
    StructField("unit_of_measure", StringType(), True),
    StructField("unit_of_measure_id", IntegerType(), True),
    StructField("Exchange_Rate", FloatType(), True),
    StructField("Terminated", StringType(), True),
    StructField("Decimal_Places", IntegerType(), True)
])

csv_foreign_exchange_path = "33100036-eng/33100036-treated.csv"
df = spark.read.csv(csv_foreign_exchange_path, schema=schema, header=True)
df = df.withColumn("date", to_date(col("date"), "yyyy-MM-dd"))

# Filter for USD exchange rate during the COVID-19 period (March 2020 to June 2021)
df_covid_usd = df.filter(
    (col("currency") == "U.S. dollar, daily average") & 
    (col("date") >= "2020-03-01") & (col("date") <= "2021-06-30")
)

# groupBy groups all rows that fall within the same month
# date_format formats the date column to display only the year and month
# avg calculates the average exchange rate for each month
df_covid_usd_monthly_avg = df_covid_usd.groupBy(date_format(col("date"), "yyyy-MM").alias("Month")).agg(
    avg("Exchange_Rate").alias("Average_USD_Monthly")
)

# Define a window to calculate the previous month's exchange rate
window_spec = Window.orderBy("Month")

# Calculate the month-over-month percentage change
df_covid_usd_monthly_avg = df_covid_usd_monthly_avg.withColumn(
    "Monthly_USD_Percent_Change",
    when(
        lag("Average_USD_Monthly").over(window_spec).isNull(), 0.0 # Case where there is no previous month
    ).otherwise(
        ((col("Average_USD_Monthly") - lag("Average_USD_Monthly").over(window_spec)) / lag("Average_USD_Monthly").over(window_spec)) * 100
    )
)

# Format the output columns for better readability
df_covid_usd_monthly_avg = df_covid_usd_monthly_avg.select(
    col("Month"),
    format_number("Average_USD_Monthly", 4).alias("Average_USD_Monthly"),
    format_number("Monthly_USD_Percent_Change", 4).alias("Monthly_USD_Percent_Change")
)

# Filter for EUR exchange rate during the COVID-19 period (March 2020 to June 2021)
df_covid_eur = df.filter(
    (col("currency") == "European euro, daily average") & 
    (col("date") >= "2020-03-01") & (col("date") <= "2021-06-30")
)

# groupBy groups all rows that fall within the same month
# date_format formats the date column to display only the year and month
# avg calculates the average exchange rate for each month
df_covid_eur_monthly_avg = df_covid_eur.groupBy(date_format(col("date"), "yyyy-MM").alias("Month")).agg(
    avg("Exchange_Rate").alias("Average_EUR_Monthly")
)

# Define a window to calculate the previous month's exchange rate
window_spec = Window.orderBy("Month")

# Calculate the month-over-month percentage change
df_covid_eur_monthly_avg = df_covid_eur_monthly_avg.withColumn(
    "Monthly_EUR_Percent_Change",
    when(
        lag("Average_EUR_Monthly").over(window_spec).isNull(), 0.0 # Case where there is no previous month
    ).otherwise(
        ((col("Average_EUR_Monthly") - lag("Average_EUR_Monthly").over(window_spec)) / lag("Average_EUR_Monthly").over(window_spec)) * 100
    )
)

# Format the output columns for better readability
df_covid_eur_monthly_avg = df_covid_eur_monthly_avg.select(
    col("Month"),
    format_number("Average_EUR_Monthly", 4).alias("Average_EUR_Monthly"),
    format_number("Monthly_EUR_Percent_Change", 4).alias("Monthly_EUR_Percent_Change")
)

# List of DataFrames to merge
dataframes = [df_covid_usd_monthly_avg, df_covid_eur_monthly_avg]

# Start with the first DataFrame
df_final = dataframes[0]

# Iterate over the remaining DataFrames and join them
for df in dataframes[1:]:
    df_final = df_final.join(df, on="Month")

# Show the final merged DataFrame
df_final.show()