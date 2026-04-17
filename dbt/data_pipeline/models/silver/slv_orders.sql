
select *
from {{ source('bronze', 'postgres_public_orders') }}
limit 100
