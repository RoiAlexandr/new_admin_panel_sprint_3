import dotenv
from pydantic import (BaseSettings, Field)

dotenv.load_dotenv()


class Dsn(BaseSettings):
    dbname: str = Field(..., env='postgres_db')
    user: str = Field('app', env='postgres_user')
    password: str = Field(..., env='postgres_password')
    host: str = Field('127.0.0.1', env='db_host')
    port: str = Field(5432, env='db_port')


class EsBaseUrl(BaseSettings):
    """ Определяет host и port у ElasticSearch"""
    es_host: str = Field(..., env='ES_HOST')
    es_port: str = Field(9200, env='ES_PORT')

    def get_url(self):
        '''Возвращает url ElasticSearch'''
        return 'http://{}:{}'.format(self.es_host, self.es_port)


class BaseConfig(BaseSettings):
    chunk_size: int = Field(50, env='CHUNK_SIZE')
    sleep_time: float = Field(60.0, env='ETL_SLEEP')
    es_base_url: str = EsBaseUrl().get_url()
    dsn: dict = Dsn().dict()
