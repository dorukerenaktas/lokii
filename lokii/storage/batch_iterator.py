from lokii.config import CONFIG

from lokii.storage.data_storage import DataStorage


class BatchIterator:
    """
    :var data_storage: database storage client
    :type data_storage: DataStorage
    :var node_name: name of the node
    :type node_name: str
    :var cur_batch: current batch index
    :type cur_batch: int
    """

    def __init__(self, data_storage, node_name):
        """
        :param data_storage: database storage client
        :type data_storage: DataStorage
        :param node_name: name of the node
        :type node_name: str
        """
        self.data_storage = data_storage
        self.node_name = node_name
        self.cur_batch = 0

    def __iter__(self):
        return self

    def __next__(self):
        q = "SELECT * FROM %s" % self.node_name
        data = self.data_storage.exec(q, self.cur_batch, CONFIG.gen.batch_size)
        if len(data) > 0:
            self.cur_batch += 1
            return data
        raise StopIteration
