# controller.py

from tkinter import filedialog, messagebox
from gui import AddDepartmentDialog, AddPersonDialog, AssignPersonDialog,AssignSearchDialog,DeletePersonDialog
from PersonDetailDialog import PersonDetailDialog

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)
        self.refresh_tree_view()

    def refresh_tree_view(self):
        """从模型获取数据并刷新组织树视图。"""
        root_data = self.model.root_department.to_dict()
        self.view.refresh_department_tree(root_data)

    def on_department_select(self, event):
        """当用户在Treeview中选择一个部门时触发。"""
        dept_id = self.view.get_selected_department_id()
        if not dept_id:
            return

        department = self.model.find_department(dept_id)
        if department:
            self.view.display_department_details(department.role_categories,department.roles)
        else:
            self.view.display_department_details(None)
        self.view.show_status(f"已选择部门: {department.name if department else 'None'}")

    def add_department(self):
        """处理添加部门的逻辑。"""
        parent_id = self.view.get_selected_department_id()
        if not parent_id:
            parent_id = "root"
            parent_name = self.model.root_department.name
        else:
            parent_dept = self.model.find_department(parent_id)
            parent_name = parent_dept.name

        dialog = AddDepartmentDialog(self.view, title="添加新部门", parent_name=parent_name)
        if dialog.dept_name:
            new_dept = self.model.add_department(dialog.dept_name, parent_id)
            if new_dept:
                self.refresh_tree_view()
                self.view.show_status(f"成功添加部门: {new_dept.name}")
            else:
                messagebox.showerror("错误", "添加部门失败！")

    def add_person(self):
        """处理添加新人员的逻辑。"""
        dialog = AddPersonDialog(self.view, title="添加新人员")
        if dialog.result:
            data = dialog.result
            if not all([data["员工ID"], data["姓名"]]):
                messagebox.showerror("错误", "员工ID和姓名不能为空！")
                return

            new_person = self.model.add_person(data["员工ID"], data["姓名"], data["年龄"], data["性别"],
                                               data["电话号码"])
            if new_person:
                self.view.show_status(f"成功添加人员: {new_person.name}")
            else:
                messagebox.showerror("错误", f"员工ID '{data['员工ID']}' 已存在！")

    def assign_person(self):
        """处理分配人员到部门的逻辑。"""
        dept_id = self.view.get_selected_department_id()
        if not dept_id:
            messagebox.showwarning("提示", "请先在组织结构树中选择一个部门！")
            return

        department = self.model.find_department(dept_id)
        all_people = list(self.model.personnel_roster.values())

        dialog = AssignPersonDialog(self.view, "分配职位", all_people, department.name)
        if dialog.result:
            data = dialog.result
            if not all([data["employee_id"], data["role_category"], data["position_title"]]):
                messagebox.showerror("错误", "所有字段都不能为空！")
                return

            success = self.model.assign_person_to_department(
                data["employee_id"],
                dept_id,
                data["role_category"],
                data["position_title"]
            )
            if success:
                self.view.show_status(f"职位分配成功！")
                # 刷新部门详情
                self.view.display_department_details(department.role_categories)
            else:
                messagebox.showerror("错误", "职位分配失败，请检查控制台输出。")

    def search_person(self):
        """调出人员查看/搜索对话框。"""
        # 这个方法现在只负责打开主查找窗口
        AssignSearchDialog(self.view, title="查看与查找员工", controller=self)

    def get_all_people(self) -> list:
        """
        从模型获取所有人员列表，用于视图显示。
        :return: Person 对象列表。
        """
        return self.model.get_all_people()


    def execute_person_search(self, name_to_search: str) -> list:
        """
        执行员工搜索的核心逻辑。
        此方法由视图(AssignSearchDialog)调用。

        :param name_to_search: 要搜索的员工姓名。
        :return: 从模型返回的搜索结果列表。
        """
        if not name_to_search:
            return []

        # 逻辑核心：调用模型的方法
        search_results = self.model.find_person_by_name(name_to_search)


        print(f"执行搜索，关键词: '{name_to_search}', 找到 {len(search_results)} 条记录。")

        return search_results
    def save_data(self):
        filepath = filedialog.asksaveasfilename(
            title="保存数据文件",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            self.model.save_to_file(filepath)
            self.view.show_status(f"数据已保存到 {filepath}")

    def load_data(self):
        filepath = filedialog.askopenfilename(
            title="加载数据文件",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            self.model.load_from_file(filepath)
            self.refresh_tree_view()
            self.view.display_department_details(None)  # Clear details panel
            self.view.show_status(f"数据已从 {filepath} 加载")

    def delete_person(self):
        """处理删除新人员的逻辑。"""
        dialog = DeletePersonDialog(self.view, title="删除人员")
        if dialog.result:
            data = dialog.result
            if not data:
                messagebox.showerror("错误", "员工ID不能为空！")
                return

            success = self.model.delete_person(data)
            if success:
                self.view.show_status(f"成功删除人员: {data}")

                ##清空详情面板
                self.view.display_department_details(None)

                current_dept_id = self.view.get_selected_department_id()
                if current_dept_id:
                    # 从模型中获取该部门更新后的数据
                    department = self.model.find_department(current_dept_id)
                    if department:
                        # 命令视图使用新数据刷新部门详情列表
                        self.view.display_department_details(department.role_categories)
            else:
                messagebox.showerror("错误", f"员工ID '{data}' 不存在！")

    def delete_department(self):
        """处理删除部门的逻辑。"""
        dept_id = self.view.get_selected_department_id()
        if not dept_id:
            messagebox.showwarning("提示", "请先在组织结构树中选择一个部门！")
            return

        department = self.model.find_department(dept_id)
        department_name = department.name
        is_confirmed = messagebox.askyesno(
            title="确认删除",
            message=f"您真的要删除部门 '{department_name}' 吗？此操作无法撤销。",
            parent=self.view
        )
        if is_confirmed:
            success = self.model.delete_department(dept_id)
            if success:
                #更新可视化界面
                self.refresh_tree_view()
                self.view.show_status(f"成功删除部门: {department_name}")
            else:
                messagebox.showerror("错误", f"删除部门 '{department_name}' 失败！")

        else:
            self.view.show_status("取消删除操作。")

    def show_person_details(self, employee_id: str):
        """
        处理显示单个员工详细信息的逻辑。
        :param employee_id: 要显示详情的员工ID。
        """
        person_details = self.get_person_details_by_id(employee_id)

        if person_details:
            # 创建并显示新的详情对话框，并将控制器自身传递进去
            PersonDetailDialog(
                parent=self.view,
                title=f"员工详情 - {person_details['name']}",
                person_info=person_details,
                controller=self  # 传入控制器实例
            )
        else:
            messagebox.showerror("错误", "无法获取该员工的详细信息。")

    def get_person_details_by_id(self, employee_id: str) -> dict | None:
        """
        根据员工ID获取其格式化后的详细信息。
        :param employee_id: 员工ID
        :return: 包含员工信息的字典，或 None
        """
        person = self.model.get_person(employee_id)
        if not person:
            return None

        # 使用模型中的 find_person_by_name 方法来获取格式化好的信息
        # 因为它已经处理好了将部门对象转为名称的逻辑
        all_people_info = self.model.find_person_by_name(person.name)

        person_details = None
        for info in all_people_info:
            if info['employee_id'] == employee_id:
                person_details = info
                break
        return person_details

    def update_person_info(self, employee_id: str, new_data: dict) -> bool:
        """
        用于更新员工信息。
        由 PersonDetailDialog 调用。
        """
        return self.model.update_person_info(employee_id, new_data)

    def remove_person_assignment(self, employee_id: str, dept_name: str, position_title: str) -> bool:
        """
        用于移除员工在某个部门中的职位。
        """
        success = self.model.remove_person_assignment(employee_id, dept_name, position_title)
        if success:
            # 职位移除成功后，需要刷新主界面上可能显示的部门详情
            current_dept_id = self.view.get_selected_department_id()
            if current_dept_id:
                department = self.model.find_department(current_dept_id)
                if department:
                    self.view.display_department_details(department.role_categories, department.roles)
        return success