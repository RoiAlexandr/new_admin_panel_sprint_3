from contextlib import contextmanager

import psycopg2
from elasticsearch import Elasticsearch
from psycopg2.extras import RealDictCursor


@contextmanager
def elastic_search_connection(dsn: str):
    """Создает подключение к ElasticSearch, которое закроет на выходе"""
    es_connection = Elasticsearch(dsn)
    try:
        yield es_connection
    finally:
        es_connection.close()


@contextmanager
def postgres_connection(dsn: dict):
    """Создает подключение к PostgreSQL, которое закроет на выходе"""
    connection = psycopg2.connect(**dsn, cursor_factory=RealDictCursor)
    connection.set_session(autocommit=True)
    try:
        yield connection
    finally:
        connection.close()
