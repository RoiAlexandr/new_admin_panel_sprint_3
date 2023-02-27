import elasticsearch.exceptions
from elasticsearch import helpers, ConnectionError

from utils.backoff_util import backoff
from utils.connection_util import elastic_search_connection


class Loader:
    def __init__(self, dsn, logger) -> None:
        self.dsn = dsn
        self.logger = logger
        self.create_index('movies')

    @backoff((ConnectionError,))
    def create_index(self, index_name: str) -> None:
        """Создание ES индекса"""
        settings = {
            "refresh_interval": "1s",
            "analysis": {
                "filter": {
                    "english_stop": {
                        "type": "stop",
                        "stopwords": "_english_"
                    },
                    "english_stemmer": {
                        "type": "stemmer",
                        "language": "english"
                    },
                    "english_possessive_stemmer": {
                        "type": "stemmer",
                        "language": "possessive_english"
                    },
                    "russian_stop": {
                        "type": "stop",
                        "stopwords": "_russian_"
                    },
                    "russian_stemmer": {
                        "type": "stemmer",
                        "language": "russian"
                    }
                },
                "analyzer": {
                    "ru_en": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "english_stop",
                            "english_stemmer",
                            "english_possessive_stemmer",
                            "russian_stop",
                            "russian_stemmer"
                        ]
                    }
                }
            }
        }

        mappings = {
            "dynamic": "strict",
            "properties": {
                "id": {
                    "type": "keyword"
                },
                "imdb_rating": {
                    "type": "float"
                },
                "genre": {
                    "type": "keyword"
                },
                "title": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {
                        "raw": {
                            "type": "keyword"
                        }
                    }
                },
                "description": {
                    "type": "text",
                    "analyzer": "ru_en"
                },
                "director": {
                    "type": "text",
                    "analyzer": "ru_en"
                },
                "actors_names": {
                    "type": "text",
                    "analyzer": "ru_en"
                },
                "writers_names": {
                    "type": "text",
                    "analyzer": "ru_en"
                },
                "actors": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "id": {
                            "type": "keyword"
                        },
                        "name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                },
                "writers": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "id": {
                            "type": "keyword"
                        },
                        "name": {
                            "type": "text",
                            "analyzer": "ru_en"
                        }
                    }
                }
            },
        }

        with elastic_search_connection(self.dsn) as es:
            if not es.ping():
                raise elasticsearch.exceptions.ConnectionError
            if not es.indices.exists(index='movies'):
                es.indices.create(index=index_name, settings=settings, mappings=mappings)

    def load(self, data: list[dict]) -> None:
        """Загружаем данные пачками в ElasticSearch"""
        actions = [{'_index': 'movies', '_id': row['id'], '_source': row, } for row in data]
        with elastic_search_connection(self.dsn) as es:
            helpers.bulk(es, actions)
            self.logger.info('загружено %s строк', len(data))
