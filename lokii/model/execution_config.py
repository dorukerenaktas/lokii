from typing import TypedDict


class ExecutionConfig(TypedDict):
    process_count: int
    batch_size: int
    chunk_size: int
