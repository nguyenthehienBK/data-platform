FROM apache/airflow:3.1.5-python3.12

USER airflow
COPY requirements.txt /
RUN pip3 install --no-cache-dir -r /requirements.txt
