from src import Lokii
from src.config import LokiConfig
import unittest


class FakerToolTest(unittest.TestCase):

    def test_pass(self):
        config: LokiConfig = {
            'languages': ['en'],
            'tables': [
                {
                    'name': 'test',
                    'option': {
                        'type': 'simple',
                        'args': {
                            'count': 5
                        }
                    },
                    'cols': {
                        'rand_email': [
                            {
                                'type': 'faker',
                                'args': {
                                    'func': 'email'
                                }
                            }
                        ],
                        'rand_paragraph': [
                            {
                                'type': 'faker',
                                'args': {
                                    'func': 'paragraph',
                                    'params': {
                                        'nb_sentences': 2
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
        Lokii(config).generate()
