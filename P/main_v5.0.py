from numpy.ma.extras import in1d

try:
    import tkinter as tk
    from tkinter import messagebox, scrolledtext, filedialog
    import os
    import turtle
    import numpy as np
    import math
    import time
    import sys
    import csv

    CANVAS_SIZE = 600
    RADIUS = 230


    def show_f(self, f):
        f.lift()


    class FenZuApp():
        def fx(self, it: int, z: int):
            l = []
            import random as r

            numbers = [0] * int(it)
            flags = [False] * int(it)
            i = 0
            while i <= int(it) - 1:
                n = r.randint(1, int(it))
                if not flags[n - 1]:
                    flags[n - 1] = True
                    numbers[i] = n
                    i += 1
            for i in range(int(z)):
                a = f"第{i + 1}组:{numbers[i * 7:7 * (i + 1)]}"
                l.append(a)
            return l

        def __init__(self, frame1):
            self.frame1 = frame1
            l1 = tk.Label(self.frame1, text="人数:")
            inp = tk.Entry(self.frame1, width=CANVAS_SIZE)
            l2 = tk.Label(self.frame1, text="分组数:")
            inp2 = tk.Entry(self.frame1, width=CANVAS_SIZE)
            i1 = int(inp.get())
            i2 = int(inp2.get())
            p = tk.Listbox()
            l = self.fx(i1, i2)
            l1.pack()
            l2.pack()
            inp.pack()
            inp2.pack()
            p.pack()
            self.frame1.pack()
            for i in l:
                p.insert(tk.END, i)


    class PickerApp:
        def __init__(self, root):
            self.root = root
            root.title("上课自动抽号系统")
            ctrl = tk.Frame(root)
            ctrl.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)
            tk.Label(ctrl, text="学生名单（每行一个名字，或留空用人数）").pack(anchor="w")
            self.names_text = scrolledtext.ScrolledText(ctrl, width=30, height=15)
            self.names_text.pack()
            row = tk.Frame(ctrl)
            row.pack(fill=tk.X, pady=4)
            tk.Label(row, text="人数(若不填名单)").pack(side=tk.LEFT)
            self.count_var = tk.StringVar()
            tk.Entry(row, textvariable=self.count_var, width=6).pack(side=tk.LEFT, padx=6)
            tk.Button(ctrl, text="生成轮盘", command=self.generate_wheel).pack(fill=tk.X, pady=4)
            tk.Button(ctrl, text="开始抽取", command=self.start_spin).pack(fill=tk.X)
            tk.Button(ctrl, text="重置", command=self.reset).pack(fill=tk.X, pady=4)
            tk.Button(ctrl, text="保存名单", command=self.names_file).pack(fill=tk.X, pady=4)
            tk.Button(ctrl, text="从CSV加载名单", command=self.names_in_csv).pack(fill=tk.X, pady=4)
            tk.Button(ctrl, text="导出示例 CSV", command=self.export_example_csv).pack(fill=tk.X, pady=4)
            tk.Button(ctrl, text="查看 MIT 许可证", command=self.show_license).pack(fill=tk.X, pady=4)
            tk.Label(ctrl, text="已抽记录").pack(anchor="w", pady=(6, 0))
            self.history = tk.Listbox(ctrl, width=30, height=8)
            self.history.pack()
            try:
                self.names_text.focus_set()
            except Exception:
                pass
            self.result_var = tk.StringVar(value="结果：")
            tk.Label(ctrl, textvariable=self.result_var, fg="blue", font=("Arial", 12)).pack(pady=6)
            canvas_frame = tk.Frame(root)
            canvas_frame.pack(side=tk.RIGHT, padx=6, pady=6)
            self.canvas = tk.Canvas(canvas_frame, width=CANVAS_SIZE, height=CANVAS_SIZE)
            self.canvas.pack()
            self.screen = turtle.TurtleScreen(self.canvas)
            self.screen.bgcolor("white")
            self.screen.tracer(0, 0)
            self.drawer = turtle.RawTurtle(self.screen)
            self.drawer.hideturtle()
            self.drawer.speed(0)
            self.drawer.up()
            self.pointer = turtle.RawTurtle(self.screen)
            self.pointer.shape("triangle")
            self.pointer.shapesize(1.2, 8)
            self.pointer.color("red")
            self.pointer.up()
            self.pointer.setheading(90)
            self.pointer.goto(0, 0)
            self.pointer.showturtle()
            self.names = []
            self.sector_angle = 360
            self.spinning = False
            root.protocol("WM_DELETE_WINDOW", self.on_close)

        def generate_wheel(self):
            text = self.names_text.get("1.0", "end").strip()
            if text:
                names = [line.strip() for line in text.splitlines() if line.strip()]
            else:
                try:
                    n = int(self.count_var.get())
                    if n <= 0:
                        raise ValueError
                except Exception:
                    messagebox.showerror("错误", "请输入有效人数或提供名单。")
                    return
                names = [str(i) for i in range(1, n + 1)]
            if len(names) == 0:
                messagebox.showerror("错误", "名单为空。")
                return
            self.names = names
            self.sector_angle = 360.0 / len(self.names)
            self.draw_wheel()
            self.result_var.set("结果：")
            self.history.delete(0, tk.END)

        def draw_wheel(self):
            self.drawer.clear()
            self.drawer.goto(0, -RADIUS)
            self.drawer.setheading(0)
            self.drawer.pendown()
            self.drawer.pensize(2)
            self.drawer.circle(RADIUS)
            self.drawer.penup()
            for i, name in enumerate(self.names):
                angle = 90 - (i * self.sector_angle + self.sector_angle / 2)
                rad = math.radians(angle)
                x = math.cos(rad) * (RADIUS - 40)
                y = math.sin(rad) * (RADIUS - 40)
                self.drawer.goto(x, y)
                self.drawer.setheading(angle - 90)
                try:
                    self.drawer.write(name, align="center", font=("Arial", 12, "normal"))
                except Exception:
                    self.screen.getcanvas().create_text(CANVAS_SIZE // 2 + x, CANVAS_SIZE // 2 - y,
                                                        text=name, fill="black", font=("Arial", 12))
            self.drawer.goto(0, 0)
            self.drawer.dot(8, "black")
            self.pointer.goto(0, 0)
            self.pointer.setheading(90)
            self.screen.update()

        def start_spin(self):
            if self.spinning:
                return
            if not self.names:
                self.generate_wheel()
                if not self.names:
                    return
            target_index = int(np.random.randint(0, len(self.names)))
            self.spinning = True
            self.result_var.set("抽取中...")
            target_angle = 90 - (target_index * self.sector_angle + self.sector_angle / 2)
            full_rotations = np.random.randint(3, 7)
            start_heading = self.pointer.heading()
            desired_final = start_heading + (full_rotations * 360) + (target_angle - start_heading)
            steps = 120
            duration = 3.0
            interval = int((duration / steps) * 1000)
            step = 0

            def animate():
                nonlocal step
                if not self.spinning:
                    return
                t = step / steps
                ease = 1 - pow(1 - t, 3)
                current = start_heading + (desired_final - start_heading) * ease
                self.pointer.setheading(current)
                self.screen.update()
                step += 1
                if step <= steps:
                    self.root.after(interval, animate)
                else:
                    self.spinning = False
                    chosen = self.names[target_index]
                    self.result_var.set(f"结果：{chosen}")
                    self.history.insert(0, chosen)

            animate()

        def reset(self):
            self.names = []
            self.drawer.clear()
            try:
                self.pointer.reset()
            except Exception:
                pass
            self.pointer = turtle.RawTurtle(self.screen)
            self.pointer.shape("triangle")
            self.pointer.shapesize(1.2, 8)
            self.pointer.color("red")
            self.pointer.up()
            self.pointer.setheading(90)
            self.pointer.goto(0, 0)
            self.pointer.showturtle()
            self.screen.update()
            self.result_var.set("结果：")
            self.history.delete(0, tk.END)
            self.names_text.delete("1.0", "end")
            self.count_var.set("")

        def on_close(self):
            try:
                self.spinning = False
                try:
                    self.screen.bye()
                except Exception:
                    pass
                try:
                    messagebox.showinfo("提示", "欢迎下次使用！", parent=self.root)
                    os.system("taskkill /F /IM python.exe")
                except Exception:

                    pass
            except Exception:
                pass
            try:
                self.root.destroy()
            except Exception:
                pass

        def names_file(self):
            text = self.names_text.get("1.0", "end").strip()
            if not text:
                try:
                    messagebox.showwarning("提示", "名单为空，未保存。", parent=self.root)
                except Exception:
                    pass
                return
            names = [line.strip() for line in text.splitlines() if line.strip()]
            path = filedialog.asksaveasfilename(
                title="保存为 CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialdir=os.getcwd(),
                parent=self.root,
            )
            if not path:
                return
            try:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    for name in names:
                        writer.writerow([name])
                try:
                    messagebox.showinfo("提示", f"已保存 {len(names)} 条名单到 {os.path.basename(path)}",
                                        parent=self.root)
                except Exception:
                    pass
            except Exception as e:
                try:
                    messagebox.showerror("错误", f"保存失败：{e}", parent=self.root)
                except Exception:
                    pass

        def names_in_csv(self):
            path = filedialog.askopenfilename(
                title="选择 CSV 文件",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialdir=os.getcwd(),
                parent=self.root,
            )
            if not path:
                return
            try:
                col = tk.simpledialog.askinteger("列选择", "请输入要读取的列号（1 表示第一列）:", parent=self.root,
                                                 minvalue=1)
            except Exception:
                col = None
            if not col:
                col = 1
            col_index = col - 1
            try:
                with open(path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    names = []
                    for row in reader:
                        if not row:
                            continue
                        cell = row[col_index] if col_index < len(row) else ""
                        cell = cell.strip()
                        if not cell:
                            continue
                        if cell.startswith("#"):
                            continue
                        names.append(cell)
            except FileNotFoundError:
                try:
                    messagebox.showwarning("提示", f"文件未找到：{path}", parent=self.root)
                except Exception:
                    pass
                return
            except Exception as e:
                try:
                    messagebox.showerror("错误", f"读取失败：{e}", parent=self.root)
                except Exception:
                    pass
                return
            if not names:
                try:
                    messagebox.showwarning("提示", "CSV 中没有有效名单。", parent=self.root)
                except Exception:
                    pass
                return
            self.names = names
            self.sector_angle = 360.0 / len(self.names)
            try:
                self.names_text.delete("1.0", "end")
                self.names_text.insert("1.0", "\n".join(names))
            except Exception:
                pass
            try:
                self.draw_wheel()
                self.history.delete(0, tk.END)
                self.result_var.set("结果：")
                messagebox.showinfo("提示", f"已从 {os.path.basename(path)} 加载 {len(names)} 条名单。",
                                    parent=self.root)
            except Exception:
                pass

        def export_example_csv(self):
            example = ['name1', 'name2', 'name3', 'name4', 'name5', 'name6', 'name7', 'name8', 'name9', 'name10']
            path = filedialog.asksaveasfilename(
                title="导出示例 CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialdir=os.getcwd(),
                parent=self.root,
            )
            if not path:
                return
            try:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    for name in example:
                        writer.writerow([name])
                try:
                    messagebox.showinfo("提示", f"示例 CSV 已导出到 {os.path.basename(path)}", parent=self.root)
                except Exception:
                    pass
            except Exception as e:
                try:
                    messagebox.showerror("错误", f"导出失败：{e}", parent=self.root)
                except Exception:
                    pass

        def show_license(self):
            lic = '''MIT License

Copyright (c) dzmmc

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
            try:
                win = tk.Toplevel(self.root)
                win.title("MIT 许可证")
                txt = scrolledtext.ScrolledText(win, width=80, height=20)
                txt.pack(padx=8, pady=8, fill=tk.BOTH, expand=True)
                txt.insert('1.0', lic)
                txt.config(state='disabled')
                tk.Button(win, text="关闭", command=win.destroy).pack(pady=6)
            except Exception:
                try:
                    messagebox.showinfo("MIT 许可证", lic, parent=self.root)
                except Exception:
                    pass


    class CmdApp:
        def __init__(self, root):
            print("欢迎使用cmd版上课自动抽号系统！")
            a = input("人数：\n")
            try:
                n = int(a)
                if n <= 0:
                    raise ValueError
            except ValueError:
                print("无效人数，程序退出。")
                sys.exit(1)
                return
            while True:
                b = input("开始抽取请按回车键(输入q退出)：\n")
                if b == "q":
                    print("退出程序。")
                    print("欢迎下次使用！")
                    sys.exit(0)
                    break
                print(f"抽取 {n} 名学生...")
                r = np.random.randint(1, n + 1)
                print(f"结果：{r}")


    if __name__ == "__main__":
        print('版权所有（C） dzmmc。保留所有权利。\n该程序python驱动，由dzmmc开发和维护。\n该程序遵守MIT许可证。')
        if len(sys.argv) > 1 and sys.argv[1].lower() in ("2", "cli", "cmd"):
            CmdApp(None)
        else:
            root = tk.Tk()
            try:
                root.withdraw()
                choice = messagebox.askquestion("选择", "模式选择\n(是=图形界面, 否=命令行)", parent=root)
                root.deiconify()
            except Exception:
                choice = "no"
            if choice == "no":
                root.destroy()
                CmdApp(None)
            else:

                messagebox.showinfo("欢迎使用——dzm",
                                    "欢迎使用上课自动抽号系统！\n请在左侧输入学生名单或人数，然后点击“生成轮盘”开始。",
                                        parent=root)
                app = PickerApp(root)
                try:
                    app.names_text.focus_set()
                except Exception:
                    pass

                root.mainloop()
except Exception as e:

    messagebox.showerror("发生【系统、文件级】错误",
                         f"错误：{e}\n可能发生的【系统、文件级】^错误：\n键盘中断，系统死机、关机，图形界面不可用（如远程终端、服务器），Windows版本过低，等。)\n^:python无法处理此类错误，如果发生请尝试使用【源代码】.py --cython-->>>【源代码】.c")
    sys.exit(1)
