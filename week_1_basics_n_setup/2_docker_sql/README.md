## Docker and SQL

Notes I used for preparing the videos: [link](https://docs.google.com/document/d/e/2PACX-1vRJUuGfzgIdbkalPgg2nQ884CnZkCg314T_OBq-_hfcowPxNIA0-z5OtMTDzuzute9VBHMjNYZFTCc1/pub)


## Commands 

All the commands from the video

Downloading the data (Linux only)

```bash
wget https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2021-01.csv
```

### Running Postgres with Docker

#### Windows

Running postgres on windows (note the full path)

Note that cmd must be run from the \ny_taxi_postgres_data folder

```bash
docker run -it ^
  -e POSTGRES_USER="root" ^
  -e POSTGRES_PASSWORD="root" ^
  -e POSTGRES_DB="ny_taxi" ^
  -v "C:\Users\[insert full path here]data-engineering-zoomcamp\week_1_basics_n_setup\2_docker_sql\ny_taxi_postgres_data":/var/lib/postgresql/data ^
  -p 5432:5432 ^
  postgres:13
```

Troubleshooting

If you have the following error:

```bash
docker run -it ^
  -e POSTGRES_USER="root" ^
  -e POSTGRES_PASSWORD="root" ^
  -e POSTGRES_DB="ny_taxi" ^
  -v e:/zoomcamp/data_engineer/week_1_fundamentals/2_docker_sql/ny_taxi_postgres_data:/var/lib/postgresql/data  ^
  -p 5432:5432 ^
  postgres:13

docker: Error response from daemon: invalid mode: ^Program Files\Git\var\lib\postgresql\data.
See 'docker run --help'.
```

Change the mounting path. Replace it with the following:

```
-p /e/zoomcamp/...:/var/lib/postgresql/data
```

#### Linux and MacOS


```bash
docker run -it ^
  -e POSTGRES_USER="root" ^
  -e POSTGRES_PASSWORD="root" ^
  -e POSTGRES_DB="ny_taxi" ^
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data ^
  -p 5432:5432 ^
  postgres:13
```

Troubleshooting

If you see that `ny_taxi_postgres_data` is empty after running
the container, try these:

* Deleting the folder and running Docker again (Docker will re-create the folder)
* Adjust the permissions of the folder by running `sudo chmod  a+rwx ny_taxi_postgres_data`


### CLI for Postgres

Installing pgcli

```bash
pip install pgcli
```

Troubleshooting

If you have problems installing pgcli with the command above, try this:

```bash
conda install -c conda-forge pgcli
pip install -U mycli
```

Using pgcli to connect to postgres

```bash
pgcli -h localhost -p 5432 -u root -d ny_taxi
```


### NY Trips Dataset

Dataset:

* https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page
* https://www1.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf


### pgAdmin

Running pgAdmin

```bash
docker run -it ^
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" ^
  -e PGADMIN_DEFAULT_PASSWORD="root" ^
  -p 8080:80 ^
  dpage/pgadmin4
```

### Running Postgres and pgAdmin together

Create a network

```bash
docker network create pg-network
```

Run Postgres (change the path)

Note that cmd must be run from the \ny_taxi_postgres_data folder

```bash
docker run -it ^
  -e POSTGRES_USER="root" ^
  -e POSTGRES_PASSWORD="root" ^
  -e POSTGRES_DB="ny_taxi" ^
  -v "C:\Users\[insert full path here]\data-engineering-zoomcamp\week_1_basics_n_setup\2_docker_sql\ny_taxi_postgres_data":/var/lib/postgresql/data ^
  -p 5432:5432 ^
  --network=pg-network ^
  --name pg-database ^
  postgres:13
```

Run pgAdmin

```bash
docker run -it ^
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" ^
  -e PGADMIN_DEFAULT_PASSWORD="root" ^
  -p 8080:80 ^
  --network=pg-network ^
  --name pgadmin-2 ^
  dpage/pgadmin4
```


### Data ingestion

PowerShell (Windows)

No URL is specified and as such the CSV must be manually downloaded and renamed to output.csv

```bash
python ingest_data.py `
  --user=root `
  --password=root `
  --host=localhost `
  --port=5432 `
  --database=ny_taxi `
  --table=yellow_taxi_trips
```

Running locally

```bash
URL="https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2021-01.csv" ^

python ingest_data.py ^
  --user=root ^
  --password=root ^
  --host=localhost ^
  --port=5432 ^
  --db=ny_taxi ^
  --table_name=yellow_taxi_trips ^
  --url=${URL}
```

Command Prompt (Windows)

```bash
python ingest_data.py ^
  --user=root ^
  --password=root ^
  --host=localhost ^
  --port=5432 ^
  --database=ny_taxi ^
  --table=yellow_taxi_trips ^
  --url="https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2021-01.csv"
```

Build the image

```bash
docker build -t taxi_ingest:v001 .
```

On Linux you may have a problem building it:

```
error checking context: 'can't stat '/home/name/data_engineering/ny_taxi_postgres_data''.
```

You can solve it with `.dockerignore`:

* Create a folder `data`
* Move `ny_taxi_postgres_data` to `data` (you might need to use `sudo` for that)
* Map `-v $(pwd)/data/ny_taxi_postgres_data:/var/lib/postgresql/data`
* Create a file `.dockerignore` and add `data` there
* Check [this video](https://www.youtube.com/watch?v=tOr4hTsHOzU&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb) (the middle) for more details 



Run the script with Docker

```bash
URL="http://172.24.208.1:8000/yellow_tripdata_2021-01.csv"

docker run -it ^
  --network=pg-network ^
  taxi_ingest:v001 ^
    --user=root ^
    --password=root ^
    --host=pg-database ^
    --port=5432 ^
    --db=ny_taxi ^
    --table_name=yellow_taxi_trips ^
    --url=${URL}
```

### Docker-Compose 

Run it:

```bash
docker-compose up
```

Run in detached mode:

```bash
docker-compose up -d
```

Shutting it down:

```bash
docker-compose down
```

Note: to make pgAdmin configuration persistent, mount a volume to the `/var/lib/pgadmin` folder:

```yaml
services:
  pgadmin:
    image: dpage/pgadmin4
    volumes:
      - ./data_pgadmin:/var/lib/pgadmin
    ...
```


### SQL 

1. Combine the trips and zones data to collect details about trips and their pickup and dropoff locations.
```sql
SELECT 
  trips.tpep_pickup_datetime
  , trips.tpep_dropoff_datetime
  , trips.total_amount
  , trips."PULocationID"
  , trips."DOLocationID"
  , CONCAT(pickup."Borough", ' ', pickup."Zone") AS pickup_location
  , CONCAT(dropoff."Borough", ' ', dropoff."Zone") AS dropoff_location
FROM
  yellow_taxi_trips trips
  , zones pickup
  , zones dropoff
WHERE
  1 = 1
  AND trips."PULocationID" = pickup."LocationID"
  AND trips."DOLocationID" = dropoff."LocationID"
LIMIT 100
;
```

Note that this does not use a left join and will not account for any discrepancies between the zones in the trips table and the zones in the zones table.

2. Validate data integrity by checking if there are any zones in the trips data that are not in the zones data. 
```sql
SELECT 
  trips.tpep_pickup_datetime
  , trips.tpep_dropoff_datetime
  , trips.total_amount
  , trips."PULocationID"
  , trips."DOLocationID"
FROM
  yellow_taxi_trips trips
WHERE
  1 = 1
  AND "DOLocationID" NOT IN (
  	SELECT "LocationID" FROM zones
  )
;
```

```sql
SELECT 
  trips.tpep_pickup_datetime
  , trips.tpep_dropoff_datetime
  , trips.total_amount
  , trips."PULocationID"
  , trips."DOLocationID"
FROM
  yellow_taxi_trips trips
WHERE
  1 = 1
  AND "PULocationID" NOT IN (
  	SELECT "LocationID" FROM zones
  )
;
```

3. Return the trip counts by date.
```sql
SELECT
  CAST(tpep_dropoff_datetime AS DATE) AS date
  , COUNT(*) AS trips
FROM
  yellow_taxi_trips trips
GROUP BY
  date
ORDER BY
  date ASC  
```

What if we wanted to return the specific zones and metric associated?
```sql
SELECT
  CAST(trips.tpep_dropoff_datetime AS DATE) date
  , trips."DOLocationID"
  , zones."Zone"
  , COUNT(*) total_trips
  , MAX(trips.total_amount) max_total_amount
  , MAX(trips.passenger_count) max_passenger_count
FROM
  yellow_taxi_trips trips
  LEFT JOIN zones
  ON trips."DOLocationID" = zones."LocationID"
GROUP BY
  1, 2, 3
ORDER BY
  1 ASC
  , 2 ASC
  , 4 DESC
  , 5 ASC
```