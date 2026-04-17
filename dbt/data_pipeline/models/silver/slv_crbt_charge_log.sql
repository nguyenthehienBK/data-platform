
select *
from {{ source('bronze', 'pg_crbt_charge_log') }}
limit 100
