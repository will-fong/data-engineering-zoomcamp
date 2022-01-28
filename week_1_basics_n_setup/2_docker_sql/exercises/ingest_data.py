# %%
import argparse as arg
import os

# %%
import pandas as pd

# %%
from time import time

# %%
from sqlalchemy import create_engine

# %%
def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    database = params.database
    table = params.table
    url = params.url

    csv = 'output.csv'

    os.system(f'wget {url} -O {csv}')

    # %%
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

    # %%
    df_iter = pd.read_csv(csv, iterator=True, chunksize=100000)

    # %%
    df = next(df_iter)

    # %%
    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    # %%
    df.head(n=0).to_sql(name=table, con=engine, if_exists='replace')

    # %%
    df.to_sql(name=table, con=engine, if_exists='append')

    # %%
    while True: 
        try:
            t_start = time()

            df = next(df_iter)

            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            
            df.to_sql(name=table, con=engine, if_exists='append')

            t_end = time()

            print('Inserted another data chunk with duration of %.3f seconds' % (t_end - t_start))

        except StopIteration:
            print('Finished iterating over all data chunks')
            break

# %%
if __name__ == '__main__':

    # %%
    parser = arg.ArgumentParser(description='This is for data ingestion from CSV to PostgreSQL')

    # %%
    parser.add_argument('--user', help='This is the user name for PostgreSQL')
    parser.add_argument('--password', help='This is the password for PostgreSQL')
    parser.add_argument('--host', help='This is the host for PostgreSQL')
    parser.add_argument('--port', help='This is the port for PostgreSQL')
    parser.add_argument('--database', help='This is the database name for PostgreSQL')
    parser.add_argument('--table', help='This is the table name for PostgreSQL')
    parser.add_argument('--url', help='This is the URL for the csv for PostgreSQL')

    # %%
    args = parser.parse_args()

    # %%
    main(args)

