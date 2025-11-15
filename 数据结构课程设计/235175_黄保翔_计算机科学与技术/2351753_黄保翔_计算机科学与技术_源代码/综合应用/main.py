# main.py

import tkinter as tk
from OrgModel import OrgModel
from gui import MainApplication
from controller import Controller

if __name__ == "__main__":
    # 1. 创建 Tkinter 根窗口
    root = tk.Tk()
    root.title("高校组织机构管理系统")
    root.geometry("1000x700")

    # 2. 实例化 MVC 组件
    model = OrgModel()
    view = MainApplication(master=root)
    controller = Controller(model, view)

    # 3. 启动主事件循环
    root.mainloop()