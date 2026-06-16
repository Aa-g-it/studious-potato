import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import random
from typing import List, Dict
import tkinter

class GroupingSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("抽号与分组系统")
        self.geometry("800x600")
        self.minsize(600, 400)

        # 初始化数据存储
        self.participants: List[str] = []
        self.groups: Dict[str, List[str]] = {}

        # 创建UI布局
        self._create_widgets()

    def _create_widgets(self):
        """创建所有UI组件"""
        # 1. 顶部控制区
        control_frame = ttk.Frame(self, padding="10")
        control_frame.pack(fill="x", expand=False)

        # 参与人数输入
        ttk.Label(control_frame, text="参与人数:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.participant_count = ttk.Spinbox(control_frame, from_=2, to=1000, width=10)
        self.participant_count.grid(row=0, column=1, padx=5, pady=5)
        self.participant_count.insert(0, "20")

        # 每组人数输入
        ttk.Label(control_frame, text="每组人数:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.group_size = ttk.Spinbox(control_frame, from_=1, to=100, width=10)
        self.group_size.grid(row=0, column=3, padx=5, pady=5)
        self.group_size.insert(0, "5")

        # 操作按钮
        self.generate_btn = ttk.Button(control_frame, text="生成分组", command=self.generate_groups)
        self.generate_btn.grid(row=0, column=4, padx=10, pady=5)

        self.export_btn = ttk.Button(control_frame, text="导出分组结果", command=self.export_to_excel, state="disabled")
        self.export_btn.grid(row=0, column=5, padx=10, pady=5)

        # 2. 结果展示区
        result_frame = ttk.Frame(self, padding="10")
        result_frame.pack(fill="both", expand=True)

        ttk.Label(result_frame, text="分组结果:").pack(anchor="w", pady=(0, 5))

        # 结果表格
        self.result_tree = ttk.Treeview(result_frame, columns=("组号", "成员列表"), show="headings")
        self.result_tree.heading("组号", text="组号")
        self.result_tree.heading("成员列表", text="成员列表")
        self.result_tree.column("组号", width=80, anchor="center")
        self.result_tree.column("成员列表", stretch=True, anchor="w")
        self.result_tree.pack(fill="both", expand=True, pady=(0, 5))

        # 滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.result_tree.configure(yscrollcommand=scrollbar.set)

    def generate_groups(self):
        """生成随机分组"""
        try:
            # 获取输入参数
            total = int(self.participant_count.get())
            size = int(self.group_size.get())

            if size <= 0 or total < size:
                messagebox.showerror("错误", "每组人数必须大于0且不超过总人数")
                return

            # 生成参与者列表（这里用编号代替实际姓名，可根据需求修改）
            self.participants = [f"成员{i + 1}" for i in range(total)]
            random.shuffle(self.participants)

            # 分组计算
            self.groups = {}
            group_num = 1
            for i in range(0, total, size):
                group_members = self.participants[i:i + size]
                self.groups[f"第{group_num}组"] = group_members
                group_num += 1

            # 更新表格显示
            self._update_result_table()

            # 启用导出按钮
            self.export_btn.config(state="normal")
            messagebox.showinfo("成功", f"已生成{len(self.groups)}个分组")

        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    def _update_result_table(self):
        """更新结果表格显示"""
        # 清空现有内容
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        # 插入新数据
        for group_name, members in self.groups.items():
            member_str = ", ".join(members)
            self.result_tree.insert("", "end", values=(group_name, member_str))

    def export_to_excel(self):
        """将分组结果导出为XLSX文件"""
        if not self.groups:
            messagebox.showwarning("提示", "没有可导出的分组数据")
            return

        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx")],
            title="保存分组结果"
        )

        if not file_path:
            return  # 用户取消保存

        try:
            export_data = []
            for group_name, members in self.groups.items():
                for member in members:
                    export_data.append({
                        "组号": group_name,
                         "成员姓名": member
                    })

            # 转换为DataFrame并导出
            df = pd.DataFrame(export_data)
            df.to_excel(file_path, index=False, sheet_name="分组结果")

            messagebox.showinfo("成功", f"分组结果已成功导出到:\n{file_path}")

        except Exception as e:
            messagebox.showerror("导出失败", f"导出过程中发生错误:\n{str(e)}")


if __name__ == "__main__":
    app = GroupingSystem()
    app.mainloop()