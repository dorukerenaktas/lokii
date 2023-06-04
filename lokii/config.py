from os import path, environ, cpu_count
import lokii

# temp directory that contains generated runtime files and database
TEMP_DIR_PATH = environ.get("LOKII__TEMP_DIR_PATH", ".temp")
# duckdb database that stores generated data in relational tables
TEMP_DB_FILE = environ.get("LOKII__TEMP_DB_FILE", "lokii.duckdb")
# name of the temp data file that contains generated runtime files
TEMP_DATA_DIR = environ.get("LOKII__TEMP_DATA_DIR", "data")

# file extension to look for when finding generation node files
GEN_NODE_EXT = environ.get("LOKII__GEN_NODE_EXT", ".node.py")
# file extension to look for when finding generation group files
GEN_GROUP_EXT = environ.get("LOKII__GEN_GROUP_EXT", ".group.py")
# -
GEN_CONCURRENCY = environ.get("LOKII__GEN_CONCURRENCY", cpu_count())
# -
GEN_BATCH_SIZE = environ.get("LOKII__GEN_BATCH_SIZE", 100000)
# -
GEN_CHUNK_SIZE = environ.get("LOKII__GEN_CHUNK_SIZE", 200)


class __Config:
    class __TempConfig:
        """
        Global configuration for storing temp file paths.
        """

        @property
        def dir_path(self) -> str:
            return TEMP_DIR_PATH

        @property
        def db_path(self) -> str:
            return path.join(TEMP_DIR_PATH, TEMP_DB_FILE)

        @property
        def data_path(self) -> str:
            return path.join(TEMP_DIR_PATH, TEMP_DATA_DIR)

    class __GenConfig:
        """
        Global configuration for storing generation information.
        """

        @property
        def node_ext(self) -> str:
            return GEN_NODE_EXT

        @property
        def group_ext(self) -> str:
            return GEN_GROUP_EXT

        @property
        def concurrency(self) -> int:
            return int(GEN_CONCURRENCY)

        @property
        def batch_size(self) -> int:
            return int(GEN_BATCH_SIZE)

        @property
        def chunk_size(self) -> int:
            return int(GEN_CHUNK_SIZE)

    @property
    def version(self):
        return lokii.__version__

    @property
    def temp(self):
        return self.__TempConfig()

    @property
    def gen(self):
        return self.__GenConfig()


CONFIG = __Config()
