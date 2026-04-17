from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Taller4Local") \
    .master("local[*]") \
    .config("spark.driver.host", "127.0.0.1") \
    .getOrCreate()

df = spark.read.csv("/data/ventas.csv", header=True, inferSchema=True)
df.show(5)
df.printSchema()

spark.stop()