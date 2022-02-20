select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

select *
from `positive-leaf-340006`.`dbt_wfong`.`stg_green_tripdata`
where tripid is null



      
    ) dbt_internal_test