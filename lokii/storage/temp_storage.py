import os
import json

from lokii.config import CONFIG


class TempStorage:
    def __init__(self, node_name: str):
        """
        Temporary filesystem storage implementation for storing data generated between batches.
        It only stores data temporary and deletes all files after node generation completed.
        :param node_name: name of the node
        """
        self.node_name = node_name
        self.batches = []
        self.item_count = 0

    def dump(self, batch_data: list[dict]) -> None:
        storage_key = self.node_name + str(len(self.batches))
        storage_path = os.path.join(CONFIG.temp.data_path, "%s.json" % storage_key)

        with open(storage_path, "w") as _f:
            _f.write(json.dumps(batch_data))

        self.batches.append(storage_path)
        self.item_count = len(batch_data)
