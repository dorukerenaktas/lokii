# Project Configuration File

Project configuration file is an optional file that used for configure and extend capabilities of the `Lokii`.
`Lokii` searches the root directory for a file with `.conf.py` extension. If it can not find one, command line
parameters or default values will be used for execution.

## File Structure

> Only global python packages can be imported to this file. 

```python
#> .project_name.conf.py

conf = {}

def prep_extras():
    pass
```

## Conventions

* Project configuration file names defines the project name.
