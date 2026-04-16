#!/usr/bin/env python3
"""WordCount en PySpark — Taller 3.

Ejecuta el mismo conteo de palabras que el job MapReduce del Taller 2
pero usando Spark, para comparar codigo, tiempo y enfoque.
"""

from pyspark.sql import SparkSession

HDFS_INPUT  = "hdfs://namenode:9000/user/root/wordcount/input"
HDFS_OUTPUT = "hdfs://namenode:9000/user/root/wordcount/output-spark"


def main():
    spark = (
        SparkSession.builder
        .appName("WordCount-Spark")
        .master("spark://spark-master:7077")
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    # Leer los mismos archivos que MapReduce del Taller 2
    text = spark.sparkContext.textFile(HDFS_INPUT)

    # Contar palabras (equivalente al mapper + reducer de MapReduce)
    counts = (
        text
        .flatMap(lambda line: line.lower().split())
        .map(lambda word: (word.strip(".,;:!?\"'()[]"), 1))
        .filter(lambda kv: len(kv[0]) > 0)
        .reduceByKey(lambda a, b: a + b)
        .sortBy(lambda kv: kv[1], ascending=False)
    )

    # Guardar en HDFS (mismo formato que MapReduce: "palabra\tconteo")
    counts.map(lambda kv: f"{kv[0]}\t{kv[1]}").saveAsTextFile(HDFS_OUTPUT)

    print("\n=== Top 30 palabras (Spark) ===")
    for word, count in counts.take(30):
        print(f"{word}\t{count}")

    spark.stop()


if __name__ == "__main__":
    main()
