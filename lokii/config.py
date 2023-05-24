import os
from pathlib import Path

root = Path(__file__).resolve().parent.parent
# read app version from root of the project
VERSION = (root / "VERSION").read_text(encoding="utf-8").strip()

# temp directory that contains generated runtime files and database
TEMP_DIR_PATH = os.environ.get("LOKII__TEMP_DIR_PATH", ".temp")
# duckdb database that stores generated data in relational tables
TEMP_DB_FILE = os.environ.get("LOKII__TEMP_DB_FILE", "lokii.duckdb")
# name of the temp data file that contains generated runtime files
TEMP_DATA_DIR = os.environ.get("LOKII__TEMP_DATA_DIR", "data")
# remove database after generation is completed
TEMP_PURGE = os.environ.get("LOKII__TEMP_PURGE", "False")

# file extension to look for when finding generation config files
GEN_FILE_EXT = os.environ.get("LOKII__GEN_FILE_EXT", ".gen.py")
# -
GEN_CONCURRENCY = os.environ.get("LOKII__GEN_CONCURRENCY", os.cpu_count())
# -
GEN_BATCH_SIZE = os.environ.get("LOKII__GEN_BATCH_SIZE", 100_000)
# -
GEN_CHUNK_SIZE = os.environ.get("LOKII__GEN_CHUNK_SIZE", 200)


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
            return os.path.join(TEMP_DIR_PATH, TEMP_DB_FILE)

        @property
        def data_path(self) -> str:
            return os.path.join(TEMP_DIR_PATH, TEMP_DATA_DIR)

        @property
        def purge(self) -> bool:
            return TEMP_PURGE != "False"

    class __GenConfig:
        """
        Global configuration for storing generation information.
        """

        @property
        def file_ext(self) -> str:
            return GEN_FILE_EXT

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
        return VERSION

    @property
    def temp(self):
        return self.__TempConfig()

    @property
    def gen(self):
        return self.__GenConfig()


CONFIG = __Config()
