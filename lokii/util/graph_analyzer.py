from collections import defaultdict


class GraphAnalyzer:
    def __init__(self, nodes: list[(str, list[str])]):
        """
        Reads and validates dataset configuration from filesystem structure.

        :param nodes: root path of the dataset generation schema
        """
        self.graph = defaultdict(list)
        self.nodes = []
        for node, deps in nodes:
            self.nodes.append(node)
            self.graph[node].extend(deps)

    def __cycle(self, index, node, visited, stack):
        visited[index] = True
        stack[index] = True

        for neighbour in self.graph[node]:
            n_index = self.nodes.index(neighbour)
            if not visited[n_index]:
                if self.__cycle(n_index, neighbour, visited, stack):
                    return True
            elif stack[n_index]:
                return True
        stack[index] = False
        return False

    def check_cyclic(self):
        length = len(self.nodes) + 1
        visited = [False] * length
        stack = [False] * length
        for index, node in enumerate(self.nodes):
            if not visited[index] and self.__cycle(index, node, visited, stack):
                raise AssertionError("Found cyclic dependencies!\n%s" % node)

    def __sort(self, index, node, visited, stack):
        visited[index] = True
        for element in self.graph[node]:
            e_index = self.nodes.index(element)
            if not visited[e_index]:
                self.__sort(e_index, element, visited, stack)
        stack.insert(0, node)

    def topological_sort(self):
        stack = []
        visited = [False] * len(self.nodes)
        for index, node in enumerate(self.nodes):
            if not visited[index]:
                self.__sort(index, node, visited, stack)
        return stack[::-1]

    def dependencies(self, name: str) -> list[str]:
        stack = []
        visited = [False] * len(self.nodes)
        index = self.nodes.index(name)
        self.__sort(index, name, visited, stack)
        return stack[::-1]

    def execution_order(self) -> list[str]:
        self.check_cyclic()
        return self.topological_sort()
