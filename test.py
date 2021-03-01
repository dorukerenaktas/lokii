from typing import Dict

from faker import Faker

from lokii import Lokii


if __name__ == '__main__':
    lokii = Lokii(debug=False)

    f = Faker()
    fakes = {
        'en': Faker(['en']),
        'tr': Faker(['tr'])
    }

    def gen_user(i: int, r: Dict):
        return {
            'id': i,
            'name': f.first_name(),
            'surname': f.last_name(),
        }

    user_table = lokii.table('common.user') \
        .cols('id', 'name', 'surname') \
        .simple(10000000, gen_user)


    def gen_lecture(i: int, r: Dict):
        return {
            'id': i,
            'code': f.random.randint(1, 1000),
        }

    lecture_table = lokii.table('common.lecture') \
        .cols('id', 'code') \
        .simple(10000000, gen_lecture)

    lecture_translate_table = lokii.table('common.lecture_translate') \
        .cols('id', 'fk_lecture_id', 'lang_code', 'name') \
        .multiply(lecture_table, lambda i, m, r: {
            'id': i,
            'fk_lecture_id': r['common.lecture']['id'],
            'lang_code': m,
            'name': fakes[m].words(nb=5)
        }, ['en', 'tr'])

    lecture_user_relation_table = lokii.table('common.lecture_user_rel') \
        .cols('id', 'fk_lecture_id', 'fk_user_id') \
        .rel(lecture_table, user_table) \
        .simple(10000000, lambda i, r: {
            'id': i,
            'fk_lecture_id': r['common.lecture']['id'],
            'fk_user_id': r['common.user']['id'],
        })
