
select *
from {{ source('bronze', 'pg_crbt_sub_collection_logs') }}
limit 100
