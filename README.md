# lokii

Generate fake datasets with ease.

## Dataset Configuration

Define a dataset by using folder and special files. Specify schemas using `schema_name` folders, configure generation
parameters using `table_name.json` and write generation scripts to `table_name.py`.

```
root_folder
    ├── schema_1
    │   ├── table_1.json
    │   ├── table_1.py
    │   ├── table_2.json
    │   └── table_2.py
    └── schema_2
        ├── table_3.json
        ├── table_3.py
        ├── table_4.json
        └── table_4.py
```

### Schema Folders

Tabular data must have a `schema` in many database environments. If your dataset does not take advantage of schema
structures just use a placeholder name like `public` in Postgres or `dbo` in SQLServer.

Create a folder for every schema in your dataset. Store table definition and table generation files under related
schema folder.

### Table Definition Files

Table definition files stores metadata and generation configuration for the tabular data. Database names are extracted
from filenames.

```json5
// table_name.json
{
  "cols": ["col1", "col2", "..."],
  "gen": {
    "type": "simple",
    "count": 1000
  }
}
```

#### Properties

##### cols
> required, type: `List[str]`

Stores column names of the table. Used for output metadata and result check assertions.

---

##### gen
> required, type: `object`

Generation config for detection generation order and generation function parameters.

---

##### gen.type
> required, type: `"simple" | "multiply"`

Generation type of the tabular data. Each option has own required properties.

* `"simple"`: used for generating standalone table data that can be executed without any other table dependencies (If
    it has no relations.).
* `"multiply"`: used for generating relational table data that needs other tables for generation function.

##### gen.count
> required if `gen.type="simple"`, type: `int`

Number of rows to be produced. Can not be used with `gen.type="multiply"`.

##### gen.mul
> required if `gen.type="multiply"`, type: `List | str`

Table namespace or a list that used as multiplier. Each item or row in multiplier will trigger current table's
generation function. Can not be used with `gen.type="simple"`.

##### gen.rels
> not required, type: `List[str]`

Table relations that used on generation function. 

### Generation Files

Generation files contains simple function that executed for each row.

```python
# table_name.py
from typing import Dict, Any

"""
:param index: row index for this table
:param config: generation config that includes relations, multiplicand and other settings
"""
def gen(index: int, config: Dict[str, Any]) -> Dict:
    return {"index": index, "config": config}
```


## Upload to PyPI
You can create the source distribution of the package by running the command given below:
```shell
python3 setup.py sdist
```

Install twine and upload pypi for `finnetdevlab` username.
```shell
pip3 install twine
twine upload dist/*
```


## Package

Basic structure of package is

```
├── README.md
├── packagename
│   ├── __init__.py
│   ├── packagename.py
│   └── version.py
├── pytest.ini
├── requirements.txt
├── setup.py
└── tests
    ├── __init__.py
    ├── helpers
    │   ├── __init__.py
    │   └── my_helper.py
    ├── tests_helper.py
    └── unit
        ├── __init__.py
        ├── test_example.py
        └── test_version.py
```

## Requirements

Package requirements are handled using pip. To install them do

```
pip install -r requirements.txt
```

## Tests

Testing is set up using [pytest](http://pytest.org) and coverage is handled
with the pytest-cov plugin.

Run your tests with ```py.test``` in the root directory.

Coverage is ran by default and is set in the ```pytest.ini``` file.
To see an html output of coverage open ```htmlcov/index.html``` after running the tests.

## Travis CI

There is a ```.travis.yml``` file that is set up to run your tests for python 2.7
and python 3.2, should you choose to use it.
