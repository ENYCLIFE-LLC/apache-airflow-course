from airflow import settings
from airflow.models import Connection
from airflow.hooks.http_hook import HttpHook
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.utils.decorators import apply_defaults

from airflow.exceptions import AirflowException


class CustomAPICallOperator(SimpleHttpOperator):
    """
    
    """
    BASE_API_URL="https://api.github.com"
    template_fields = ['endpoint', 'data']
    
    @apply_defaults # decorator to make sure the __init__ method is called with the right arguments
    def __init__(
        self,
        base_url,
        conn_host,
        endpoint,
        method,
        data=None,
        headers=None,
        response_check=None,
        extra_options=None,
        http_conn_id='http_default',
        log_response=False,
        *args, **kwargs
    ) -> None:
        self.http_conn_id = http_conn_id
        self.method=method,
        self.endpoint=endpoint,
        self.headers=headers,
        self.data = data,
        self.response_check = response_check,
        self.etra_options = extra_options,
        self.log_response = log_response
        self.conn_host = conn_host
        
        super(CustomAPICallOperator).__init__(
            endpoint=endpoint,
            method=method,
            data=data,
            headers=headers,
            response_check=response_check,
            extra_options=extra_options,
            xcom_push=True,
            http_conn_id=http_conn_id,
            log_response=log_response,
            *args, **kwargs
        )
        self.base_url = base_url
        self.conn_host = conn_host
        
    
    
    def _get_http_conn(self, conn_type="HTTP", login=None, password=None, port=None):
        conn = Connection(
            conn_id=self.http_conn_id,
            conn_type=conn_type,
            host=self.conn_host,
            login=login,
            password=password,
            port=port
        )
        session = settings.Session()
        session.add(conn)
        session.commit()
        return conn
    
    
    def execute(self, context):
        http = HttpHook(
            method=self.method,
            http_conn_id=self.http_conn_id,
            headers=self.headers,
            data=self.data
        )
        response = http.run(self.endpoint)
        if response.status_code < 200 or response.status_code > 299:
            raise AirflowException(f"Http request failed, status code: {response.status_code}")
        
        if self.log_response:
            self.log.info(response.text)
        if self.response_check:
            if not self.response_check(response):
                raise AirflowException("Response check returned False.")
        return response.text
    
    
    def rm_conn(self):
        session = settings.Session()
        conn = session.query(Connection).filter(Connection.conn_id == self.http_conn_id).first()
        session.delete(conn)
        session.commit()
        return conn