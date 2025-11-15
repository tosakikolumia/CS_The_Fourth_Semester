import tkinter as tk
from gui import MainApplication

if __name__ == "__main__":
    root = tk.Tk()
    root.title("有向图分析工具")
    app = MainApplication(master=root)
    app.mainloop()