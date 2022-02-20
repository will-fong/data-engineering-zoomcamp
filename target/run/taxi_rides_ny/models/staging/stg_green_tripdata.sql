

  create or replace view `positive-leaf-340006`.`dbt_wfong`.`stg_green_tripdata`
  OPTIONS()
  as 

select * from `positive-leaf-340006`.`trips_data_all`.`green_tripdata`
limit 100;

