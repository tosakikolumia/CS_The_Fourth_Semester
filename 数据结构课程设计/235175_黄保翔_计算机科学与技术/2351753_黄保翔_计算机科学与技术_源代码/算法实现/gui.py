# gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from graph import Graph
import math


class MainApplication(tk.Frame):
    """
    主窗口类
    """
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.graph = Graph()
        self.master.title("有向图分析工具 (Directed Graph Analysis Tool)")
        self.master.geometry("1200x800")
        self.pack(fill="both", expand=True)


        self.node_positions = {}
        self.node_radius = 20
        self.drawn_items = {}


        self.topo_steps = []
        self.current_topo_step = 0

        self._create_widgets()

    def _create_widgets(self):
        """Creates and lays out all the GUI widgets."""

        control_frame = ttk.Frame(self, padding="10")
        control_frame.pack(side="top", fill="x")

        display_frame = ttk.Frame(self)
        display_frame.pack(side="top", fill="both", expand=True)


        paned_window = ttk.PanedWindow(display_frame, orient='horizontal')
        paned_window.pack(fill='both', expand=True, padx=10, pady=5)


        canvas_frame = ttk.Frame(paned_window)
        self.canvas = tk.Canvas(canvas_frame, bg="#f0f0f0", highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        paned_window.add(canvas_frame, weight=3)  # Give more weight to the canvas


        notebook_frame = ttk.Frame(paned_window)
        notebook = ttk.Notebook(notebook_frame)


        tab1 = ttk.Frame(notebook)
        adj_label = ttk.Label(tab1, text="邻接链表 (Adjacency List):")
        adj_label.pack(anchor='w', padx=5, pady=(5, 0))
        self.adj_text = tk.Text(tab1, height=10, width=40, font=("Courier", 10))
        self.adj_text.pack(fill='both', expand=True, padx=5, pady=5)

        topo_label = ttk.Label(tab1, text="拓扑排序结果 (Topological Sort Result):")
        topo_label.pack(anchor='w', padx=5, pady=(5, 0))
        self.topo_text = tk.Text(tab1, height=4, width=40)
        self.topo_text.pack(fill='x', expand=False, padx=5, pady=5)
        notebook.add(tab1, text='基本信息')


        tab2 = ttk.Frame(notebook)
        cp_label = ttk.Label(tab2, text="关键路径分析 (Critical Path Analysis):")
        cp_label.pack(anchor='w', padx=5, pady=(5, 0))
        cols = ('Activity', 'E', 'L', 'Slack', 'Critical')
        self.cp_tree = ttk.Treeview(tab2, columns=cols, show='headings')
        for col in cols:
            self.cp_tree.heading(col, text=col)
            self.cp_tree.column(col, width=60, anchor='center')
        self.cp_tree.pack(fill='both', expand=True, padx=5, pady=5)
        notebook.add(tab2, text='关键路径')

        notebook.pack(fill='both', expand=True)
        paned_window.add(notebook_frame, weight=2)


        input_label = ttk.Label(control_frame, text="输入图 (格式: a b 5):")
        input_label.pack(side="left", padx=(0, 5))

        self.input_text = tk.Text(control_frame, height=5, width=30)
        self.input_text.pack(side="left", fill="x", expand=True)
        self.input_text.insert("1.0", "A B 6\nA C 4\nA D 5\nB E 1\nC E 1\nD F 2\nE G 9\nE H 7\nF H 4\nG I 2\nH I 4")

        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side="left", padx=10)

        self.btn_generate = ttk.Button(button_frame, text="生成/清空图", command=self._generate_graph)
        self.btn_generate.grid(row=0, column=0, padx=5, pady=2, sticky='ew')

        self.btn_topo_step = ttk.Button(button_frame, text="拓扑排序(单步)", command=self._run_topo_sort_step,
                                        state="disabled")
        self.btn_topo_step.grid(row=0, column=1, padx=5, pady=2, sticky='ew')

        self.btn_topo_run = ttk.Button(button_frame, text="拓扑排序(自动)", command=self._run_topo_sort_auto,
                                       state="disabled")
        self.btn_topo_run.grid(row=1, column=1, padx=5, pady=2, sticky='ew')

        self.btn_cp = ttk.Button(button_frame, text="计算关键路径", command=self._calculate_critical_path,
                                 state="disabled")
        self.btn_cp.grid(row=0, column=2, padx=5, pady=2, sticky='ew')


        self.status_var = tk.StringVar(value="准备就绪 (Ready)")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w')
        status_bar.pack(side="bottom", fill="x")

    def _generate_graph(self):
        """
        生成/清空图按钮事件处理函数
        解析输入文本框中的图数据，生成图对象，并清空画布、邻接链表、拓扑排序结果、关键路径分析树视图等内容
        """
        self._clear_all()
        self.graph.clear()

        input_data = self.input_text.get("1.0", "end-1c").strip()
        if not input_data:
            self.status_var.set("输入为空 (Input is empty)")
            return

        try:
            edges = input_data.split('\n')
            for edge in edges:
                parts = edge.strip().split()
                if len(parts) == 3:
                    u, v, w = parts[0], parts[1], int(parts[2])
                    self.graph.add_edge(u, v, w)
                elif len(parts) == 2:  # Default weight 1 if not provided
                    u, v = parts[0], parts[1]
                    self.graph.add_edge(u, v, 1)
        except (ValueError, IndexError) as e:
            messagebox.showerror("输入错误", f"输入格式错误: {e}\n请遵循 '起点 终点 权重' 格式.")
            return

        self._display_adjacency_list()
        self._calculate_node_positions()
        self._draw_graph()

        # Enable algorithm buttons
        self.btn_topo_step.config(state="normal")
        self.btn_topo_run.config(state="normal")
        self.btn_cp.config(state="normal")
        self.status_var.set(
            f"图已生成: {len(self.graph.nodes)} 个节点 (Graph generated: {len(self.graph.nodes)} nodes)")

    def _clear_all(self):
        """
        清空所有内容，包括画布、邻接链表、拓扑排序结果、关键路径分析树视图等内容，并重置
        """
        self.canvas.delete("all")
        self.adj_text.delete("1.0", "end")
        self.topo_text.delete("1.0", "end")
        for i in self.cp_tree.get_children():
            self.cp_tree.delete(i)

        self.node_positions = {}
        self.drawn_items = {'nodes': {}, 'edges': {}, 'labels': {}}
        self.current_topo_step = 0
        self.topo_steps = []

        self.btn_topo_step.config(state="disabled")
        self.btn_topo_run.config(state="disabled")
        self.btn_cp.config(state="disabled")
        self.status_var.set("准备就绪 (Ready)")

    def _display_adjacency_list(self):
        """展示邻接链表"""
        self.adj_text.delete("1.0", "end")
        text = ""
        sorted_nodes = sorted(list(self.graph.adjacency_list.keys()))
        for node in sorted_nodes:
            neighbors = ", ".join([f"{v}({w})" for v, w in self.graph.adjacency_list[node]])
            text += f"{node} -> {neighbors}\n"
        self.adj_text.insert("1.0", text)

    def _calculate_node_positions(self):
        """计算节点位置"""
        self.node_positions.clear()
        nodes = sorted(list(self.graph.nodes))
        count = len(nodes)
        if count == 0:
            return

        center_x = self.canvas.winfo_width() / 2
        center_y = self.canvas.winfo_height() / 2
        radius = min(center_x, center_y) * 0.75

        for i, node in enumerate(nodes):
            angle = (2 * math.pi / count) * i
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.node_positions[node] = (x, y)

    def _draw_graph(self):
        """删除之前的图，重新画图"""
        self.canvas.delete("all")
        self.drawn_items = {'nodes': {}, 'edges': {}, 'labels': {}}

        if not self.node_positions: self._calculate_node_positions()


        for u, pos_u in self.node_positions.items():
            for v, weight in self.graph.adjacency_list[u]:
                if v in self.node_positions:
                    pos_v = self.node_positions[v]
                    edge = self.canvas.create_line(pos_u[0], pos_u[1], pos_v[0], pos_v[1], arrow=tk.LAST, fill="gray",
                                                   width=1.5)
                    self.drawn_items['edges'][(u, v)] = edge


        for node, pos in self.node_positions.items():
            x, y = pos

            oval = self.canvas.create_oval(x - self.node_radius, y - self.node_radius,
                                           x + self.node_radius, y + self.node_radius,
                                           fill="lightblue", outline="black")

            self.canvas.create_text(x, y, text=node, font=("Arial", 12, "bold"))

            in_degree = self.graph.in_degree.get(node, 0)
            label = self.canvas.create_text(x, y + self.node_radius + 10, text=f"in:{in_degree}", fill="darkblue")

            self.drawn_items['nodes'][node] = oval
            self.drawn_items['labels'][node] = {'in_degree': label}

    def _run_topo_sort_step(self, auto_run=False):
        """执行单步拓扑排序"""
        if self.current_topo_step == 0 and not self.topo_steps:
            # First step: initialize
            self.topo_text.delete("1.0", "end")
            topo_order, self.topo_steps, is_dag = self.graph.topological_sort()
            if not is_dag:
                messagebox.showerror("错误", "图中存在环，无法进行拓扑排序!")
                self.status_var.set("错误：检测到环")
                self.topo_steps = []
                return

        if self.current_topo_step < len(self.topo_steps):
            step_data = self.topo_steps[self.current_topo_step]
            node = step_data['processing_node']


            self.canvas.itemconfig(self.drawn_items['nodes'][node], fill="lightgreen")
            self.topo_text.insert("end", f"{node} ")


            for v, _ in self.graph.adjacency_list.get(node, []):

                edge_id = self.drawn_items['edges'][(node, v)]
                self.canvas.itemconfig(edge_id, fill="orange", width=2.5)


                new_in_degree = step_data['in_degrees'][v] - 1 if (v, _) in self.graph.adjacency_list.get(node, []) else \
                step_data['in_degrees'][v]

                next_val = 0
                if self.current_topo_step + 1 < len(self.topo_steps):
                    next_node = self.topo_steps[self.current_topo_step + 1]['processing_node']

                    for v_neighbor, _ in self.graph.adjacency_list.get(node, []):
                        if v_neighbor in self.topo_steps[self.current_topo_step]['in_degrees']:
                            current_in_deg = self.topo_steps[self.current_topo_step]['in_degrees'][v_neighbor]
                            self.canvas.itemconfig(self.drawn_items['labels'][v_neighbor]['in_degree'],
                                                   text=f"in:{current_in_deg - 1}")

            self.current_topo_step += 1
            if auto_run:
                self.master.after(1000, self._run_topo_sort_step, True)
        else:
            self.status_var.set("拓扑排序完成 (Topological sort complete)")
            self.btn_topo_run.config(state="normal")
            self.btn_topo_step.config(state="normal")

    def _run_topo_sort_auto(self):
        """执行自动拓扑排序"""
        self._draw_graph()  # Reset colors
        self.current_topo_step = 0
        self.topo_steps = []
        self.btn_topo_run.config(state="disabled")
        self.btn_topo_step.config(state="disabled")
        self._run_topo_sort_step(auto_run=True)

    def _calculate_critical_path(self):
        """计算关键路径"""
        self._draw_graph()  # Reset to default state first

        results, Ve, Vl, is_dag = self.graph.critical_path()

        if not is_dag:
            messagebox.showerror("错误", "图中存在环，无法计算关键路径!")
            self.status_var.set("错误：检测到环 (Error: Cycle detected)")
            return

        for node, pos in self.node_positions.items():
            ve_val = Ve.get(node, 0)
            vl_val = Vl.get(node, 0)
            self.canvas.create_text(pos[0] - self.node_radius - 5, pos[1], text=f"Ve:{ve_val}", anchor='e',
                                    fill="darkgreen")
            self.canvas.create_text(pos[0] + self.node_radius + 5, pos[1], text=f"Vl:{vl_val}", anchor='w',
                                    fill="maroon")

        for i in self.cp_tree.get_children():
            self.cp_tree.delete(i)

        for (u, v), data in results.items():
            is_critical_text = "Yes" if data['is_critical'] else "No"
            self.cp_tree.insert('', 'end', values=(f"{u}->{v}", data['E'], data['L'], data['Slack'], is_critical_text))

            if data['is_critical']:
                edge_id = self.drawn_items['edges'][(u, v)]
                self.canvas.itemconfig(edge_id, fill="red", width=3)
                # Highlight nodes on the critical path
                self.canvas.itemconfig(self.drawn_items['nodes'][u], fill="orangered")
                self.canvas.itemconfig(self.drawn_items['nodes'][v], fill="orangered")

        self.status_var.set("关键路径计算完成 (Critical path calculation complete)")

