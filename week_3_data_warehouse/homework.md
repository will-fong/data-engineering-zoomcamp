## Homework
[Form](https://forms.gle/ytzVYUh2RptgkvF79)  
We will use all the knowledge learned in this week. Please answer your questions via form above.  
**Deadline** for the homework is 14th Feb 2022 17:00 CET.

### Question 1: 
**What is count for fhv vehicles data for year 2019**  
Can load the data for cloud storage and run a count(*)

There are 18,954,089 trips in 2019 for For Hire Vehicles.

```sql
-- Creating external table referring to gcs path with parquet
CREATE OR REPLACE EXTERNAL TABLE `positive-leaf-340006.trips_data_all.external_fhv_tripdata`
OPTIONS (
  format = 'parquet',
  uris = [
      'gs://dtc_data_lake_positive-leaf-340006/raw/fhv_tripdata/2019/2019-*.parquet'
    --   , 'gs://dtc_data_lake_positive-leaf-340006/raw/fhv_tripdata/2020/2020-*.parquet'
      ]
);
```

```sql
-- Check FHV trip data
SELECT 
    COUNT(*) fhv_trips_total_count 
FROM positive-leaf-340006.trips_data_all.external_fhv_tripdata 
-- WHERE pickup_datetime LIKE '%2019%'
;
```

```json
[
  {
    "fhv_trips_total_count": "18954089"
  }
]
```

### Question 2: 
**How many distinct dispatching_base_num we have in fhv for 2019**  
Can run a distinct query on the table from question 1

There are 714 distinct dispatching base numbers in 2019 for For Hire Vehicles.

```sql
SELECT 
    COUNT(DISTINCT dispatching_base_num) dispatching_base_num_unique_count 
FROM positive-leaf-340006.trips_data_all.external_fhv_tripdata 
-- WHERE pickup_datetime LIKE '%2019%'
;
```

```json
[
  {
    "dispatching_base_num_unique_count": "714"
  }
]
```

### Question 3: 
**Best strategy to optimise if query always filter by dropoff_datetime and order by dispatching_base_num**  
Review partitioning and clustering video.   
We need to think what will be the most optimal strategy to improve query performance and reduce cost.

### Question 4: 
**What is the count, estimated and actual data processed for query which counts trip between 2019/01/01 and 2019/03/31 for dispatching_base_num B00987, B02060, B02279**  
Create a table with optimized clustering and partitioning, and run a count(*). Estimated data processed can be found in top right corner and actual data processed can be found after the query is executed.

There are 15,822 trips between 2019/01/01 and 2019/03/31 for the dispatch bases of B00987, B02060, and B02279.

```sql
CREATE OR REPLACE TABLE positive-leaf-340006.trips_data_all.fhv_tripdata_partitioned_clustered
PARTITION BY DATE(dropoff_datetime)
CLUSTER BY dispatching_base_num AS
    (
        SELECT * FROM positive-leaf-340006.trips_data_all.external_fhv_tripdata
    )
;
```

```sql
SELECT 
    COUNT(*) dispatching_base_num_count 
FROM positive-leaf-340006.trips_data_all.fhv_tripdata_partitioned_clustered
WHERE 
    1 = 1
    AND dropoff_datetime >= '2019-01-01' 
    AND dropoff_datetime <= '2019-03-31' 
    AND dispatching_base_num IN ('B00987', 'B02060', 'B02279')
;
```

```json
[
  {
    "dispatching_base_num_count": "15822"
  }
]
```

### Question 5: 
**What will be the best partitioning or clustering strategy when filtering on dispatching_base_num and SR_Flag**  
Review partitioning and clustering video. 
Clustering cannot be created on all data types.

### Question 6: 
**What improvements can be seen by partitioning and clustering for data size less than 1 GB**  
Partitioning and clustering also creates extra metadata.  
Before query execution this metadata needs to be processed.

### (Not required) Question 7: 
**In which format does BigQuery save data**  
Review big query internals video.
