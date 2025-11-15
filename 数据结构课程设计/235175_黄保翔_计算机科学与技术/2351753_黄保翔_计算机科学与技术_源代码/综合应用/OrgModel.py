'''数据模型管理器'''
from Department import Department
# OrgModel.py (Completed)

from Department import Department
from Person import Person
import uuid  # 用于生成唯一的部门ID
import json  # 用于保存和加载数据

class OrgModel:
    """数据模型管理器，封装所有数据操作逻辑"""

    def __init__(self):
        """初始化模型，建立一个根部门和员工线性表"""
        self.root_department: Department = Department("root", "同济大学")
        # personnel_roster 以 employee_id 为键，Person 对象为值，便于快速查找
        self.personnel_roster: dict[str, Person] = {}

    def add_person(self, employee_id, name, age, gender, phone_number):
        """
        向花名册中添加一个新职工。
        :param employee_id: 员工ID (必须唯一)
        :return: 成功则返回 Person 对象, 若ID已存在则返回 None
        """
        if employee_id in self.personnel_roster:
            print(f"错误: 员工ID '{employee_id}' 已存在。")
            return None
        new_person = Person(employee_id, name, age, gender, phone_number, [])
        print(f"2. 准备创建Person对象: ID='{employee_id}', 类型={type(employee_id)}")
        self.personnel_roster[employee_id] = new_person
        return new_person

    def delete_person(self, employee_id: str) -> bool:
        """
        从系统中彻底删除一个职工，包括从花名册和所有部门任职中。
        :param employee_id: 员工ID
        :return: 成功返回 True, 失败返回 False
        """
        if employee_id not in self.personnel_roster:
            print(f"错误: 员工ID '{employee_id}' 不存在。")
            return False

        person_to_delete = self.personnel_roster[employee_id]

        del self.personnel_roster[employee_id]

        # 首先获取包括根部门在内的所有部门列表
        all_departments = [self.root_department] + self.root_department.get_all_children()

        for dept in all_departments:
            # 遍历所有职位类别：'主管', '副主管', '其他人员'
            for category, staff_list in dept.role_categories.items():
                # 如果员工在列表中，则移除
                if person_to_delete in staff_list:
                    staff_list.remove(person_to_delete)

            # 清理 roles 字典（可选，但更严谨）
            roles_to_delete = [title for title, person in dept.roles.items() if person == person_to_delete]
            for title in roles_to_delete:
                del dept.roles[title]

        return True

    def get_person(self, employee_id: str) -> Person | None:
        """
        根据员工ID从花名册中查找员工。
        :param employee_id: 员工ID
        :return: 找到则返回 Person 对象，否则返回 None
        """
        return self.personnel_roster.get(employee_id)

    def find_department(self, department_id: str, start_node=None) -> Department | None:
        """
        在组织树中递归查找指定ID的部门。
        :param department_id: 要查找的部门ID
        :param start_node: 查找的起始节点，默认为根节点
        :return: 找到则返回 Department 对象，否则返回 None
        """
        if start_node is None:
            start_node = self.root_department

        if start_node.department_id == department_id:
            return start_node

        for child in start_node.children:
            found = self.find_department(department_id, child)
            if found:
                return found
        return None

    def add_department(self, name: str, parent_dept_id: str) -> Department | None:
        """
        动态建立组织结构，添加新部门。
        :param name: 新部门的名称
        :param parent_dept_id: 父部门的ID
        :return: 成功则返回新创建的 Department 对象，若父部门不存在则返回 None
        """
        parent_dept = self.find_department(parent_dept_id)
        if parent_dept is None:
            print(f"错误: 未找到ID为 '{parent_dept_id}' 的父部门。")
            return None

        # 使用 uuid 生成一个唯一的部门 ID
        new_dept_id = str(uuid.uuid4())
        new_department = Department(new_dept_id, name, parent=parent_dept)
        parent_dept.add_child(new_department)
        return new_department
    def delete_department(self, department_id: str) -> bool:
        """
        从组织结构中彻底删除一个部门，包括所有子部门和人员。
        :param department_id:
        :return:
        """
        # 1. 找到要删除的部门
        dept_to_delete = self.find_department(department_id)
        if dept_to_delete is None:
            print(f"错误: 未找到ID为 '{department_id}' 的部门。")
            return False
        # 2. 递归删除所有子部门
        for child in dept_to_delete.children:
            self.delete_department(child.department_id)
        # 3. 删除部门自身
        parent = dept_to_delete.parent

        if parent:
            parent.remove_child(dept_to_delete)
        else:#没有父节点，说明是根部门
            self.root_department = None
        return True
    def assign_person_to_department(self, employee_id: str, dept_id: str, role_category: str,
                                    position_title: str) -> bool:
        """
        将人员添加到部门中，并定义职位。
        :param employee_id: 员工ID
        :param dept_id: 部门ID
        :param role_category: 职位类别 ('主管', '副主管', '其他人员')
        :param position_title: 具体职位名称 (如'院长', '教授')
        :return: 成功返回 True, 失败返回 False
        """
        person = self.get_person(employee_id)
        department = self.find_department(dept_id)

        if not person or not department:
            print("错误: 员工或部门不存在。")
            return False

        if role_category not in department.role_categories:
            print(f"错误: 无效的职位类别 '{role_category}'。")
            return False

        # 处理主管职位的唯一性
        if role_category == '主管' and department.role_categories['主管']:
            print(f"错误: 部门 '{department.name}' 已存在一名主管。")
            return False

        # 在部门中记录人员和职位
        department.role_categories[role_category].append(person)
        department.roles[position_title] = person

        # 在人员信息中记录所属部门和职位
        person.add_assigment(department, position_title)

        return True

    def find_person_by_name(self, name: str) -> list:
        """
        根据输入的人员名，查找其所在的部门、职位等信息。
        :param name: 要查找的姓名
        :return: 一个包含所有匹配人员信息的列表
        """
        found_people_info = []
        for person in self.personnel_roster.values():
            if person.name == name:
                info = person.get_info()  #
                # 为了显示清晰，将 assigment 中的对象转换为名称
                info['assigment'] = [(d.name, pos) for d, pos in person.assigment]
                found_people_info.append(info)
        return found_people_info

    def get_all_people(self) -> list:
        """
        返回花名册中所有 Person 对象的列表。
        :return: 一个包含所有 Person 对象的列表。
        """
        return list(self.personnel_roster.values())

    def save_to_file(self, filepath: str):
        """
        将整个组织模型的数据保存到 JSON 文件。
        :param filepath: 文件路径 (例如 'data.json')
        """
        # 构建要保存的完整数据结构，包含人员信息和部门结构
        all_data = {
            # 1. 序列化所有人员信息
            # 使用列表推导式将人员对象转换为字典格式
            'personnel': [person.to_dict() for person in self.personnel_roster.values()],
            # 2. 序列化整个部门树结构
            'departments': self.root_department.to_dict()
        }

        try:
            # 使用 with 语句打开文件，确保文件正确关闭
            # 设置编码为 utf-8 以支持中文
            with open(filepath, 'w', encoding='utf-8') as f:
                # 使用 indent=4 美化输出，ensure_ascii=False 保证中文正常显示
                json.dump(all_data, f, indent=4, ensure_ascii=False)
            print(f"数据成功保存到 {filepath}")
        except Exception as e:
            print(f"保存失败: {e}")

        # --- 新增加载功能 ---

    def load_from_file(self, filepath: str):
        """
        从 JSON 文件加载数据并重建组织模型。
        :param filepath: 文件路径
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
        except FileNotFoundError:
            print(f"错误: 文件 {filepath} 未找到。")
            return
        except Exception as e:
            print(f"加载失败: {e}")
            return

        # 1. 清空当前模型
        self.root_department = Department("root", "同济大学")
        self.personnel_roster = {}

        # 2. 加载所有人员信息
        for person_data in all_data['personnel']:
            emp_id = person_data['employee_id']
            print(f"1. 从JSON加载: ID='{emp_id}', 类型={type(emp_id)}")
            self.add_person(
                person_data['employee_id'],
                person_data['name'],
                person_data.get('age'),
                person_data.get('gender'),
                person_data.get('phone_number')
            )

        # 3. 递归重建部门树
        if 'departments' in all_data:
            self._build_departments_recursively(all_data['departments'], self.root_department)

        # 4. 重新链接人员和部门的关系 (关键步骤)
        for person_data in all_data['personnel']:
            for assignment in person_data.get('assigment', []):
                # 找到职位类别
                dept = self.find_department(assignment['department_id'])
                if not dept: continue
                role_cat = "其他人员"  # 默认为其他
                for cat, emp_ids in all_data['departments']['role_categories'].items():
                    if person_data['employee_id'] in emp_ids:
                        role_cat = cat
                        break

                self.assign_person_to_department(
                    person_data['employee_id'],
                    assignment['department_id'],
                    role_cat,
                    assignment['position']
                )

        print(f"数据从 {filepath} 加载成功。")

    def _build_departments_recursively(self, data: dict, parent: Department):
        """用于加载的辅助函数，递归创建部门。"""
        for child_data in data['children']:
            child_dept = self.add_department(child_data['name'], parent.department_id)
            # 确保ID一致，以便后续链接
            child_dept.department_id = child_data['department_id']

            # 递归为子部门创建它们的子部门
            self._build_departments_recursively(child_data, child_dept)

    def update_person_info(self, employee_id, new_data):
        """
        更新一个员工的基本信息。
        :param employee_id: 员工ID。
        :param new_data: 包含新信息的字典, 如 {'name': '新名字', 'age': '35'}。
        :return: 成功返回 True, 失败返回 False。
        """
        person = self.get_person(employee_id)
        if not person:
            return False

        person.name = new_data.get("name", person.name)
        person.age = new_data.get("age", person.age)
        person.gender = new_data.get("gender", person.gender)
        person.phone_number = new_data.get("phone_number", person.phone_number)
        return True

    def remove_person_assignment(self, employee_id, dept_name, position_title):
        """
        移除一个员工的特定职位。
        :param employee_id: 员工ID。
        :param dept_name: 职位所在的部门名称。
        :param position_title: 职位名称。
        :return: 成功返回 True, 失败返回 False。
        """
        person = self.get_person(employee_id)
        if not person:
            return False

        # 从 Person 对象的 assigment 列表中移除
        original_len = len(person.assigment)
        person.assigment = [(d, p) for d, p in person.assigment if not (d.name == dept_name and p == position_title)]

        if len(person.assigment) == original_len:
            return False  # 没有找到匹配的职位

        # 从 Department 对象的 roles 和 role_categories 中移除
        all_departments = [self.root_department] + self.root_department.get_all_children()
        for dept in all_departments:
            if dept.name == dept_name:
                # 从 roles 字典移除
                if dept.roles.get(position_title) == person:
                    del dept.roles[position_title]
                # 从 role_categories 列表移除
                for category in dept.role_categories.values():
                    if person in category:
                        category.remove(person)
                        break
                break
        return True