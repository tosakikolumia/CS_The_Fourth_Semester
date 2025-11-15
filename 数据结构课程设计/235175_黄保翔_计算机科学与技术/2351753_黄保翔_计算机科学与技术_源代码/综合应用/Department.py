#该文件对Department类进行了定义，包括了Department类中的属性和方法。
from math import degrees


# Department.py (Corrected and Refined)

class Department:
    def __init__(self, department_id: str, name: str, parent=None):
        """
        构造函数，用于初始化 Department 对象的属性。
        :param department_id: 部门ID
        :param name: 部门名称
        :param parent:  父部门引用
        """
        self.department_id: str = department_id
        self.name: str = name
        self.parent = parent
        self.children = []
        # roles 字典用于存储担任具体职务的人员
        self.roles = {}  # 例如: {'院长': person_obj, '教学副院长': person_obj}
        # role_categories 列表用于定义部门内职务的分类
        self.role_categories = {'主管': [], '副主管': [], '其他人员': []}

    def add_child(self, child):
        """添加一个子部门"""
        if child not in self.children:
            self.children.append(child)
            child.parent = self

    def remove_child(self, child):
        """移除一个子部门"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def get_all_children(self):
        """递归获取所有层级的子部门"""
        all_children = []
        for child in self.children:
            all_children.append(child)
            all_children.extend(child.get_all_children())
        return all_children

    def to_dict(self):
        """将 Department 对象及其所有子部门递归地转换为字典。"""
        return {
            'department_id': self.department_id,
            'name': self.name,
            # 存储子部门的字典列表，而不是对象
            'children': [child.to_dict() for child in self.children],
            # 存储人员的 ID，而不是对象
            'roles': {title: person.employee_id for title, person in self.roles.items()},
            'role_categories': {
                category: [person.employee_id for person in plist]
                for category, plist in self.role_categories.items()
            }
        }