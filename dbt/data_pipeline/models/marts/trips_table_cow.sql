{{ config(
    materialized='incremental',
    file_format='hudi',
    unique_key='uuid',
    incremental_strategy='merge',
) }}

select
  *
from {{ ref('stg_trips_table_cow') }}
