import json
import os

TEMP_STORAGE_DIR = ".temp/data"


class TempBatchStorage:
    def __init__(self, node_name: str, target_count: int):
        """
        Temporary filesystem storage implementation for storing data generated between batches.
        It only stores data temporary and deletes all files after node generation completed.
        :param node_name: name of the node
        :param target_count: target loop count for the node generation
        """
        if not os.path.exists(TEMP_STORAGE_DIR):
            os.makedirs(TEMP_STORAGE_DIR)

        self.node_name = node_name
        self.target_count = target_count
        self.item_count = 0
        self.batches: list[str] = []

    def dump(self, batch_data: list[dict]) -> None:
        storage_key = self.node_name + str(len(self.batches))
        storage_path = os.path.join(TEMP_STORAGE_DIR, storage_key + ".json")

        with open(storage_path, "w") as _f:
            _f.write(json.dumps(batch_data))

        self.batches.append(storage_path)
        self.item_count = len(batch_data)

    def purge(self) -> None:
        for batch in self.batches:
            os.remove(batch)
