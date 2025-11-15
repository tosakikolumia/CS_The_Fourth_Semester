from collections import defaultdict, deque
# graph.py
# This file contains the Graph class which manages the graph's data structure
# and implements the core algorithms like topological sort and critical path.

from collections import defaultdict, deque


class Graph:
    """
    该类管理图的结构，并实现核心算法，如拓扑排序和关键路径。
    """
    def __init__(self):
        """
        初始化图的数据结构。
        """
        self.clear()

    def add_edge(self, u, v, weight):
        """
        添加一条边到图中。
        Args:
            u (int): 源节点。
            v (int): 目标节点。
            weight (int): 边的权重。

        """

        self.adjacency_list[u].append((v, weight))

        self.nodes.add(u)
        self.nodes.add(v)

        self.in_degree[v] += 1

        if u not in self.in_degree:
            self.in_degree[u] = 0

    def clear(self):
        """
        清空图的数据结构。
        """
        self.adjacency_list = defaultdict(list)
        self.nodes = set()
        self.in_degree = defaultdict(int)
        # Ve: Earliest event occurrence time (for nodes)
        self.Ve = defaultdict(int)
        # Vl: Latest event occurrence time (for nodes)
        self.Vl = defaultdict(int)

    def topological_sort(self):
        """
        对图进行拓扑排序。
        返回值：
            - list: 拓扑排序的结果。
            - list: 用于可视化的步骤。
            - bool: 如果图是DAG，则为True，否则为False。

        """

        in_degree_map = self.in_degree.copy()

        # 初始化队列
        queue = deque([node for node in self.nodes if in_degree_map[node] == 0])

        topo_order = []
        steps = []

        while queue:
            u = queue.popleft()
            topo_order.append(u)

            steps.append({
                'processing_node': u,
                'in_degrees': in_degree_map.copy()
            })

            for v, _ in self.adjacency_list[u]:
                in_degree_map[v] -= 1
                # If in-degree becomes 0, add it to the queue
                if in_degree_map[v] == 0:
                    queue.append(v)


        if len(topo_order) == len(self.nodes):
            return topo_order, steps, True  # Success
        else:
            return [], steps, False  # Cycle detected

    def critical_path(self):
        """
        这个类用于计算关键路径。
        返回值：
            - dict: 每个活动的关键路径信息。
            - dict: 每个节点的Earliest Event Time (Ve)。
            - dict: 每个节点的Latest Event Time (Vl)。
            - bool: 如果图是DAG，则为True，否则为False。
        """
        topo_order, _, is_dag = self.topological_sort()
        if not is_dag:
            print("Error: Cycle detected in graph. Cannot compute critical path.")
            return None, None, None, False

        self.Ve = defaultdict(int)
        for u in topo_order:
            for v, weight in self.adjacency_list[u]:
                if self.Ve[v] < self.Ve[u] + weight:
                    self.Ve[v] = self.Ve[u] + weight


        project_duration = max(self.Ve.values())
        self.Vl = defaultdict(lambda: project_duration)

        for u in reversed(topo_order):
            if not self.adjacency_list[u]:
                self.Vl[u] = self.Ve[u]

            for v, weight in self.adjacency_list[u]:
                if self.Vl[u] > self.Vl[v] - weight:
                    self.Vl[u] = self.Vl[v] - weight


        activity_results = {}
        for u in self.nodes:
            for v, weight in self.adjacency_list[u]:

                e_start = self.Ve[u]


                l_start = self.Vl[v] - weight


                slack = l_start - e_start

                activity_results[(u, v)] = {
                    'E': e_start,
                    'L': l_start,
                    'Slack': slack,
                    'is_critical': slack == 0
                }

        return activity_results, self.Ve, self.Vl, True