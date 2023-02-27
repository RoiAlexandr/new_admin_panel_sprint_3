import datetime
import logging
import os
import time

import elasticsearch
import psycopg2

from extractor import Extractor
from loader import Loader
from transformer import Transformer
from backoff import backoff
from storage import (State, JsonFileStorage)




@backoff((elasticsearch.exceptions.ConnectionError,))
@backoff((psycopg2.OperationalError,))
def etl(logger: logging.Logger, extracrot: Extractor, transformer: Transformer, state: State, loader: Loader) -> None:
    '''
    Extract-Transform-Load процесс перекачки данных из PostgreSQL в Elasticsearch
    '''

    last_sync_timestamp = state.get_state('last_sync_timestamp')
    start_timestamp = datetime.datetime.now()
    filmwork_ids = state.get_state('filmwork_ids')

    # извлекаем данные для переноса их из PostgreSQL в Elasticsearch
    for extracted_part in extracrot.extract(last_sync_timestamp, start_timestamp, filmwork_ids):
        # преобразовываем данные в формат, удобоваримый Elasticsearch
        data = transformer.transform(extracted_part)
        # грузим в Elasticsearch
        loader.load(data)
        # фиксируем время синхронизации
        state.set_state("last_sync_timestamp", str(start_timestamp))
        # обнуляем список filmwork_ids
        state.set_state("filmwork_ids", [])


if __name__ == '__main__':
    dsl = {'dbname': os.environ.get('DB_NAME'),
           'user': os.environ.get('DB_USER_NAME'),
           'password': os.environ.get('DB_PASSWORD'),
           'host': os.environ.get('DB_HOST'),
           'port': os.environ.get('DB_PORT')
           }

    state = State(JsonFileStorage(file_path='state.json'))
    with psycopg2.connect(**dsl) as pg_conn, pg_conn.cursor() as cursor:
        extractor = Extractor(**dsl, chunk_size=os.environ.get('SIZE'), storage_state=state)
    transformer = Transformer()
    loader = Loader(dsn=os.environ.get('ES_BASE_URL'))
    while True:
        etl(extractor, transformer, state, loader)
        time.sleep(os.environ.get('ET_SLEEP'))