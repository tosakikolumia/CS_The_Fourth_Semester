# gui.py

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.simpledialog import Dialog

class PersonDetailDialog(tk.Toplevel):
    """
    一个用于显示、更新和管理员工信息的弹出对话框。
    """

    def __init__(self, parent, title, person_info, controller):
        """
        初始化员工详情对话框。
        :param parent: 父窗口。
        :param title: 窗口标题。
        :param person_info: 包含员工详细信息的字典。
        :param controller: 控制器实例，用于执行后台操作。
        """
        super().__init__(parent)
        self.transient(parent)  # 设置为父窗口的瞬态窗口
        self.grab_set()         # 锁定焦点，实现模态效果

        self.title(title)
        self.geometry("1000x600")

        self.person_info = person_info
        self.controller = controller
        self.employee_id = person_info['employee_id']
        self.entries = {}

        self._create_widgets()
        self._populate_data()

        # 确保窗口在屏幕中央
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """创建所有UI组件。"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)

        # --- 基本信息区 ---
        info_frame = ttk.LabelFrame(main_frame, text="基本信息", padding="10")
        info_frame.pack(fill="x", expand=True)

        fields = ["员工ID", "姓名", "年龄", "性别", "电话号码"]
        # 将 person_info 的键映射到界面显示的标签
        key_map = {
            "员工ID": "employee_id", "姓名": "name", "年龄": "age",
            "性别": "gender", "电话号码": "phone_number"
        }

        for i, field in enumerate(fields):
            label = ttk.Label(info_frame, text=f"{field}:")
            label.grid(row=i, column=0, sticky="w", padx=5, pady=3)
            entry = ttk.Entry(info_frame, width=30)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=3)
            self.entries[key_map[field]] = entry

        info_frame.columnconfigure(1, weight=1)

        # --- 职位信息区 ---
        assignment_frame = ttk.LabelFrame(main_frame, text="职位信息", padding="10")
        assignment_frame.pack(fill="both", expand=True, pady=(10, 0))

        cols = ('department', 'position')
        self.assignment_tree = ttk.Treeview(assignment_frame, columns=cols, show='headings', height=5)
        self.assignment_tree.heading('department', text='所在部门')
        self.assignment_tree.heading('position', text='担任职位')
        self.assignment_tree.column('department', width=150)
        self.assignment_tree.column('position', width=150)
        self.assignment_tree.pack(side="left", fill="both", expand=True)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(assignment_frame, orient="vertical", command=self.assignment_tree.yview)
        self.assignment_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # --- 操作按钮区 ---
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=10)

        self.remove_button = ttk.Button(action_frame, text="卸任该职位", command=self._remove_assignment)
        self.remove_button.pack(side="left")

        button_bar = ttk.Frame(main_frame)
        button_bar.pack(side="bottom", fill="x", pady=(10, 0))

        self.update_button = ttk.Button(button_bar, text="更新信息", command=self._update_person_info)
        self.update_button.pack(side="right", padx=5)

        self.close_button = ttk.Button(button_bar, text="关闭", command=self.destroy)
        self.close_button.pack(side="right")

    def _populate_data(self):
        """用传入的数据填充UI组件。"""
        # 填充基本信息
        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
            # .get(key, '') 避免因数据缺失导致错误
            entry.insert(0, self.person_info.get(key, ''))

        # 将员工ID设为只读
        self.entries['employee_id'].config(state='readonly')

        # 填充职位信息
        for i in self.assignment_tree.get_children():
            self.assignment_tree.delete(i)

        for dept_name, position in self.person_info.get('assigment', []):
            self.assignment_tree.insert("", "end", values=(dept_name, position))

    def _update_person_info(self):
        """收集输入框数据并调用控制器进行更新。"""
        new_data = {key: entry.get() for key, entry in self.entries.items()}

        success = self.controller.update_person_info(self.employee_id, new_data)
        if success:
            messagebox.showinfo("成功", "员工信息更新成功！", parent=self)
            self.destroy()  # 更新成功后关闭窗口
        else:
            messagebox.showerror("失败", "员工信息更新失败，请检查数据或控制台输出。", parent=self)

    def _remove_assignment(self):
        """处理卸任职位的逻辑。"""
        selection = self.assignment_tree.selection()
        if not selection:
            messagebox.showwarning("未选择", "请先在列表中选择一个要卸任的职位。", parent=self)
            return

        selected_item = self.assignment_tree.item(selection[0])
        dept_name, position_title = selected_item['values']

        is_confirmed = messagebox.askyesno(
            "确认卸任",
            f"确定要让该员工从【{dept_name}】卸任【{position_title}】一职吗？",
            parent=self
        )

        if not is_confirmed:
            return

        success = self.controller.remove_person_assignment(self.employee_id, dept_name, str(position_title))

        if success:
            messagebox.showinfo("成功", "职位已成功卸任。", parent=self)
            # 刷新UI以反映变化
            # 从模型重新获取最新的员工信息
            self.person_info = self.controller.get_person_details_by_id(self.employee_id)
            # 重新填充整个对话框的数据
            self._populate_data()
        else:
            messagebox.showerror("失败", "职位卸任失败，该职位可能不存在或已移除。", parent=self)