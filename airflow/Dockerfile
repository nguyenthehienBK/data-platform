FROM apache/airflow:2.10.4

USER airflow
COPY requirements.txt /
RUN pip3 install --no-cache-dir -r /requirements.txt
