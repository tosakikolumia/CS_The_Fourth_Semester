#该文件对Person类进行了定义，包括构造函数、属性和方法。
from operator import ifloordiv


class Person:
    def __init__(self,employee_id, name, age, gender,phone_number,assigment): #构造函数，用于初始化Person对象的属性
        '''
        :param employee_id: 员工id
        :param name: 姓名
        :param age: 年龄
        :param gender: 性别
        :param phone_number: 电话号码
        :param assigment: 所属部门列表，一个人可以所属多个部门,列表中的每一项可以是一个元组 (department_object, position_title)。
        '''
        self.employee_id:str = employee_id
        self.name = name
        self.age = age
        self.gender = gender
        self.phone_number = phone_number
        self.assigment = assigment if assigment else [] #如果assigment为空，则初始化为空列表

    def add_assigment(self, department_object, position_title): #添加所属部门的方法
        '''
        :param department_object: 部门对象
        :param position_title: 职位名称
        '''
        self.assigment.append((department_object, position_title))
    def get_info(self): #获取个人信息的方法
        #返回json格式的个人信息
        return {"employee_id":self.employee_id,"name":self.name,"age":self.age,"gender":self.gender,"phone_number":self.phone_number,"assigment":self.assigment}

    def to_dict(self):
        """将 Person 对象转换为可序列化为 JSON 的字典。"""
        # 关键点：不能直接存储 department 对象，而是存储其 ID，以便后续重构关系。
        assignments_serializable = [
            {'department_id': dept.department_id, 'position': pos}
            for dept, pos in self.assigment
        ]
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "phone_number": self.phone_number,
            "assigment": assignments_serializable
        }
