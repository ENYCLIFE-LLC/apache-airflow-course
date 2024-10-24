from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 1),
    'retries': 1,
}

def python_operator_demo():
    print("python_operator_demo is called!")

dag = DAG(
    '1_first_dag', default_args=default_args, description='My first simple DAG', schedule_interval=timedelta(days=2))

t1 = EmptyOperator(task_id='task_1', dag=dag)

t2 = PythonOperator(task_id='task_2', python_callable=python_operator_demo, dag=dag,)

t3 = EmptyOperator(task_id='task_3', dag=dag,)

t1 >> t2 >> t3


