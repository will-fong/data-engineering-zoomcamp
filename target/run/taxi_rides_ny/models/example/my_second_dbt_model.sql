

  create or replace view `positive-leaf-340006`.`dbt_wfong`.`my_second_dbt_model`
  OPTIONS()
  as -- Use the `ref` function to select from other models

select *
from `positive-leaf-340006`.`dbt_wfong`.`my_first_dbt_model`
where id = 1;

