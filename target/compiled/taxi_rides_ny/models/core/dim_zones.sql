

select 
    locationid, 
    borough, 
    zone, 
    replace(service_zone,'Boro','Green') as service_zone
from `positive-leaf-340006`.`dbt_wfong`.`taxi_zone_lookup`