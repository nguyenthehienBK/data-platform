
select
  -- `_hoodie_commit_time`, 
  -- `_hoodie_file_name`, 
  ts, 
  'uuid-012' as uuid, 
  'rider-Hien' as rider, 
  'driver-AK' as driver, 
  fare, 
  'phu_tho' as city
from {{ source('warehouse', 'trips_table_cow') }}
where uuid = 'uuid-001'