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
                                'type': 'random',
                                'args': {
                                    'func': 'random'
                                }
                            }
                        ],
                        'rand_paragraph': [
                            {
                                'type': 'random',
                                'args': {
                                    'func': 'choice',
                                    'params': {
                                        'seq': [1, 2, 3]
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
        Lokii(config).generate()
