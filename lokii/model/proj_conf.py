from typing import TypedDict, Dict


class ProjConf(TypedDict):
    """
    Defines global configuration for the dataset generation project.

    :var schema_dept: defines the nested structural level for the model structure.
    """

    schema_dept: int


ProjectConfig = Dict[str, ProjConf]


class ProjectConfigModule(TypedDict):
    """
    :var name: defines name of the project
    :var conf: defines global configuration for the dataset generation project
    """

    name: str
    conf: ProjectConfig
