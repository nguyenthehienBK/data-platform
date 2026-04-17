
select *
from {{ source('bronze', 'pg_crbt_substate_log') }}
limit 100
