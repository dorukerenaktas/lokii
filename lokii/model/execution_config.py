from typing import TypedDict


class ExecutionConfig(TypedDict):
    process_count: int
    batch_size: int
    cache_size: int
