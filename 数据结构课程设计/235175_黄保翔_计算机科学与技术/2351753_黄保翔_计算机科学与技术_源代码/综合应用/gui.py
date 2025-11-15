# gui.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.simpledialog import Dialog


class MainApplication(tk.Frame):
    """主视图类，构建所有UI组件。"""

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)
        self.controller = None
        self._create_widgets()

    def set_controller(self, controller):
        """设置控制器，并将UI事件与控制器方法绑定。"""
        self.controller = controller
        # 绑定 Treeview 的选择事件
        self.tree.bind("<<TreeviewSelect>>", self.controller.on_department_select)

    def _create_widgets(self):
        # --- Top Control Frame ---
        control_frame = ttk.Frame(self, padding="5")
        control_frame.pack(side="top", fill="x")

        ttk.Button(control_frame, text="添加部门", command=lambda: self.controller.add_department()).pack(side="left",padx=2)
        ttk.Button(control_frame, text="添加人员", command=lambda: self.controller.add_person()).pack(side="left",padx=2)
        ttk.Button(control_frame, text="分配职位", command=lambda: self.controller.assign_person()).pack(side="left", padx=2)
        ttk.Button(control_frame, text="查找人员", command=lambda: self.controller.search_person()).pack(side="left", padx=2)
        ttk.Button(control_frame, text="删除部门", command=lambda: self.controller.delete_department()).pack(side="left",padx=2)
        ttk.Button(control_frame, text="删除人员", command=lambda: self.controller.delete_person()).pack(side="left",padx=2)
        ttk.Button(control_frame, text="保存数据", command=lambda: self.controller.save_data()).pack(side="left",padx=2)
        ttk.Button(control_frame, text="加载数据", command=lambda: self.controller.load_data()).pack(side="left", padx=2)

        # --- Main Paned Window (Resizable) ---
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Left Pane: Organization Tree ---
        tree_frame = ttk.Labelframe(main_pane, text="组织结构")
        self.tree = ttk.Treeview(tree_frame, columns=("name",), show="tree headings")
        self.tree.heading("#0", text="结构", anchor='w')
        self.tree.heading("name", text="部门名称", anchor='w')
        self.tree.pack(fill="both", expand=True)
        main_pane.add(tree_frame, weight=1)

        # --- Right Pane: Details Notebook ---
        details_frame = ttk.Labelframe(main_pane, text="详细信息")
        self.notebook = ttk.Notebook(details_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        main_pane.add(details_frame, weight=2)

        # --- Department Details Tab ---
        dept_tab = ttk.Frame(self.notebook)
        self.notebook.add(dept_tab, text="部门详情")

        ttk.Label(dept_tab, text="主管:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.head_list = tk.Listbox(dept_tab, height=2)
        self.head_list.grid(row=1, column=0, sticky='ew', padx=5)

        ttk.Label(dept_tab, text="副主管:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.deputy_list = tk.Listbox(dept_tab, height=5)
        self.deputy_list.grid(row=3, column=0, sticky='ew', padx=5)

        ttk.Label(dept_tab, text="其他人员:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.staff_list = tk.Listbox(dept_tab, height=10)
        self.staff_list.grid(row=5, column=0, sticky='ew', padx=5)
        dept_tab.columnconfigure(0, weight=1)

        # --- Status Bar ---
        self.status_var = tk.StringVar(value="准备就绪")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w')
        status_bar.pack(side="bottom", fill="x")

    def show_status(self, message):
        """更新状态栏信息。"""
        self.status_var.set(message)

    def refresh_department_tree(self, root_department_data):
        """清空并用新数据刷新组织结构树。"""
        for i in self.tree.get_children():
            self.tree.delete(i)

        self._populate_tree(root_department_data, "")

    def _populate_tree(self, department_data, parent_id):
        """递归填充组织树的辅助函数。"""
        dept_id = department_data['department_id']
        dept_name = department_data['name']
        self.tree.insert(parent_id, "end", iid=dept_id, text=dept_id, values=(dept_name,))

        for child_data in department_data['children']:
            self._populate_tree(child_data, dept_id)

    def display_department_details(self, dept_details, dept_roles=None):
        """在详情面板显示部门信息。"""
        self.head_list.delete(0, tk.END)
        self.deputy_list.delete(0, tk.END)
        self.staff_list.delete(0, tk.END)

        if not dept_details:
            return

        def get_position_titles(person, dept_roles):
            titles = []
            if dept_roles:
                for title, p in dept_roles.items():
                    if hasattr(p, "employee_id") and p.employee_id == person.employee_id:
                        titles.append(title)
            return ", ".join(titles)

        head = dept_details.get('主管', [])
        for person in head:
            pos_titles = get_position_titles(person, dept_roles)
            self.head_list.insert(tk.END, f"{person.name} ({person.employee_id}) [{pos_titles}]")

        deputies = dept_details.get('副主管', [])
        for person in deputies:
            pos_titles = get_position_titles(person, dept_roles)
            self.deputy_list.insert(tk.END, f"{person.name} ({person.employee_id}) [{pos_titles}]")

        staff = dept_details.get('其他人员', [])
        for person in staff:
            pos_titles = get_position_titles(person, dept_roles)
            self.staff_list.insert(tk.END, f"{person.name} ({person.employee_id}) [{pos_titles}]")

    def get_selected_department_id(self):
        """获取当前在Treeview中选中的部门ID。"""
        selection = self.tree.selection()
        return selection[0] if selection else None


# --- 对话框类 ---

class AddDepartmentDialog(Dialog):
    def __init__(self, parent, title=None, parent_name=None):
        self.parent_name = parent_name
        self.dept_name = ""
        super().__init__(parent, title)

    def body(self, master):
        ttk.Label(master, text=f"父部门: {self.parent_name}").grid(row=0, columnspan=2)
        ttk.Label(master, text="新部门名称:").grid(row=1, sticky='w')
        self.name_entry = ttk.Entry(master)
        self.name_entry.grid(row=1, column=1)
        return self.name_entry

    def apply(self):
        self.dept_name = self.name_entry.get().strip()


class AddPersonDialog(Dialog):
    def __init__(self, parent, title=None):
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        fields = ["员工ID", "姓名", "年龄", "性别", "电话号码"]
        self.entries = {}
        for i, field in enumerate(fields):
            ttk.Label(master, text=f"{field}:").grid(row=i, column=0, sticky='w', padx=5, pady=2)
            entry = ttk.Entry(master)
            entry.grid(row=i, column=1, sticky='ew', padx=5, pady=2)
            self.entries[field] = entry
        return self.entries["员工ID"]

    def apply(self):
        self.result = {field: entry.get().strip() for field, entry in self.entries.items()}



class DeletePersonDialog(Dialog):
    def __init__(self, parent, title=None):
        # 将 result 的初始化移到这里
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        """只创建对话框的主体部分（输入控件）。"""
        ttk.Label(master, text="请输入要删除的员工ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.id_entry = ttk.Entry(master, width=30)
        self.id_entry.grid(row=0, column=1, padx=5, pady=5)

        # 返回初始时应获得焦点的控件
        return self.id_entry

    def buttonbox(self):
        """创建底部的按钮栏。"""
        box = ttk.Frame(self)

        ok_button = ttk.Button(box, text="确定", width=10, command=self.ok)
        ok_button.pack(side=tk.LEFT, padx=5, pady=5)

        cancel_button = ttk.Button(box, text="取消", width=10, command=self.cancel)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    def apply(self):
        """
        当用户点击“确定”后，此方法被自动调用。
        所有逻辑处理都应放在这里。
        """
        input_id = self.id_entry.get().strip()

        if not input_id:
            messagebox.showwarning("输入无效", "员工ID不能为空！", parent=self)
            # 让输入框重新获得焦点，阻止对话框关闭
            self.id_entry.focus_set()
            return

        is_confirmed = messagebox.askyesno(
            title="确认删除",
            message=f"您真的要删除员工 '{input_id}' 吗？此操作无法撤销。",
            parent=self
        )

        if is_confirmed:
            # 只有在最终确认后，才将结果赋值给 self.result
            self.result = input_id
        else:
            # 如果用户取消确认，让输入框重新获得焦点
            self.id_entry.focus_set()
            # 设置 self.result 为 None (或保持不变)，并阻止对话框关闭
            self.result = None
class AssignPersonDialog(Dialog):
    def __init__(self, parent, title, people_list, dept_name):
        self.people = people_list
        self.dept_name = dept_name
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        ttk.Label(master, text=f"分配到部门: {self.dept_name}").grid(row=0, columnspan=2)

        ttk.Label(master, text="选择员工:").grid(row=1, column=0, sticky='w')
        self.person_combo = ttk.Combobox(master, values=[f"{p.name} ({p.employee_id})" for p in self.people])
        self.person_combo.grid(row=1, column=1)

        ttk.Label(master, text="职位类别:").grid(row=2, column=0, sticky='w')
        self.role_cat_combo = ttk.Combobox(master, values=['主管', '副主管', '其他人员'])
        self.role_cat_combo.grid(row=2, column=1)

        ttk.Label(master, text="具体职位:").grid(row=3, column=0, sticky='w')
        self.pos_title_entry = ttk.Entry(master)
        self.pos_title_entry.grid(row=3, column=1)

        return self.person_combo

    def apply(self):
        person_str = self.person_combo.get()
        # 从 "姓名 (ID)" 格式中提取 ID
        emp_id = person_str.split('(')[-1].replace(')', '').strip()

        self.result = {
            "employee_id": emp_id,
            "role_category": self.role_cat_combo.get(),
            "position_title": self.pos_title_entry.get().strip()
        }


class AssignSearchDialog(Dialog):
    """
    一个多功能对话框：
    1. 默认显示所有人员。
    2. 支持按姓名搜索人员。
    3. 支持双击人员跳转到详情页。
    """

    def __init__(self, parent, title=None, controller=None):
        self.controller = controller
        super().__init__(parent, title)

    def body(self, master):
        """创建对话框的主体部分。"""
        # --- 搜索输入区 ---
        search_frame = ttk.Frame(master)
        search_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(search_frame, text="输入员工姓名:").pack(side='left', padx=(0, 5))
        self.name_entry = ttk.Entry(search_frame)
        self.name_entry.pack(side='left', fill='x', expand=True)
        self.search_button = ttk.Button(search_frame, text="查找", command=self._perform_search)
        self.search_button.pack(side='left', padx=(5, 0))
        self.show_all_button = ttk.Button(search_frame, text="显示全部", command=self._show_all_people)
        self.show_all_button.pack(side='left', padx=(5, 0))

        # --- 结果展示区 ---
        results_frame = ttk.Frame(master)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        cols = ('employee_id', 'name', 'age', 'gender')
        self.results_tree = ttk.Treeview(results_frame, columns=cols, show='headings')

        # 定义列标题
        self.results_tree.heading('employee_id', text='员工ID')
        self.results_tree.heading('name', text='姓名')
        self.results_tree.heading('age', text='年龄')
        self.results_tree.heading('gender', text='性别')
        self.results_tree.column('employee_id', width=100)
        self.results_tree.column('name', width=120)
        self.results_tree.column('age', width=60, anchor='center')
        self.results_tree.column('gender', width=60, anchor='center')

        # 添加滚动条
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.results_tree.pack(side='left', fill='both', expand=True)

        # 绑定双击事件
        self.results_tree.bind("<Double-1>", self._on_item_double_click)

        # 默认显示所有人员
        self._show_all_people()

        return self.name_entry

    def buttonbox(self):
        """创建底部的按钮栏。"""
        box = ttk.Frame(self)
        close_button = ttk.Button(box, text="关闭", width=10, command=self.destroy)
        close_button.pack(side=tk.RIGHT, padx=5, pady=5)
        self.bind("<Return>", lambda event: self._perform_search())
        box.pack()

    def _clear_tree(self):
        """清空 Treeview 中的所有条目。"""
        for i in self.results_tree.get_children():
            self.results_tree.delete(i)

    def _populate_tree(self, people_list):
        """用人员列表数据填充 Treeview。"""
        self._clear_tree()
        if not people_list:
            self.results_tree.insert("", "end", values=("", "未找到结果", "", ""))
        else:
            for person in people_list:
                # 重点：使用 iid=person.employee_id 来安全存储原始字符串ID
                self.results_tree.insert("", "end", iid=person.employee_id, values=(
                    person.employee_id, person.name, person.age, person.gender
                ))

    def _show_all_people(self):
        """获取并显示所有人员。"""
        all_people = self.controller.get_all_people()
        self._populate_tree(all_people)

    def _perform_search(self):
        """执行按姓名搜索的逻辑。"""
        name_to_search = self.name_entry.get().strip()
        if not name_to_search:
            self._show_all_people()
            return

        search_results_info = self.controller.execute_person_search(name_to_search)

        # 将搜索到的详细信息转换为 Person 对象列表（去重）
        found_ids = set()
        people_list = []
        for info in search_results_info:
            if info['employee_id'] not in found_ids:
                person_obj = self.controller.model.get_person(info['employee_id'])
                if person_obj:
                    people_list.append(person_obj)
                    found_ids.add(info['employee_id'])

        self._populate_tree(people_list)

    def _on_item_double_click(self, event):
        """处理双击 Treeview 条目的事件。"""
        selection = self.results_tree.selection()
        if not selection:
            return

        employee_id = selection[0]

        if employee_id is not None and employee_id != "":
            self.controller.show_person_details(employee_id)


