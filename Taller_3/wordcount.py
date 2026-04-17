#!/usr/bin/env python3
from pyspark.sql import SparkSession
def main():
    spark = SparkSession.builder.appName('WordCount-Spark').master('spark://spark-master:7077').config('spark.hadoop.fs.defaultFS', 'hdfs://namenode:9000').getOrCreate()
    spark.sparkContext.setLogLevel('WARN')
    text = spark.sparkContext.textFile('/user/root/wordcount/input')
    counts = text.flatMap(lambda line: line.lower().split()).map(lambda word: (word.strip('.,;:!?\"()[]'), 1)).filter(lambda kv: len(kv[0]) > 0).reduceByKey(lambda a, b: a + b).sortBy(lambda kv: kv[1], ascending=False)
    counts.map(lambda kv: f'{kv[0]}\t{kv[1]}').saveAsTextFile('/user/root/wordcount/output-spark')
    print('\n=== Top 30 palabras (Spark) ===')
    for word, count in counts.take(30):
        print(f'{word}\t{count}')
    spark.stop()
if __name__ == '__main__':
    main()
