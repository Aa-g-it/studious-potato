try:
    import tkinter as tk
    from tkinter import messagebox, scrolledtext
    import turtle
    import numpy as np
    import math
    import time
    import sys

    CANVAS_SIZE = 600
    RADIUS = 230

    class PickerApp:
        def __init__(self, root):
            self.root = root
            root.title("上课自动抽号系统")

            # Left: controls
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

            tk.Label(ctrl, text="已抽记录").pack(anchor="w", pady=(6,0))
            self.history = tk.Listbox(ctrl, width=30, height=8)
            self.history.pack()

            # put keyboard focus into the names text by default so users can type immediately
            try:
                self.names_text.focus_set()
            except Exception:
                pass

            # Bottom status
            self.result_var = tk.StringVar(value="结果：")
            tk.Label(ctrl, textvariable=self.result_var, fg="blue", font=("Arial", 12)).pack(pady=6)

            # Right: turtle canvas
            canvas_frame = tk.Frame(root)
            canvas_frame.pack(side=tk.RIGHT, padx=6, pady=6)
            self.canvas = tk.Canvas(canvas_frame, width=CANVAS_SIZE, height=CANVAS_SIZE)
            self.canvas.pack()

            # Turtle setup on the canvas
            self.screen = turtle.TurtleScreen(self.canvas)
            self.screen.bgcolor("white")
            self.screen.tracer(0, 0)  # manual updates

            # drawer for wheel and pointer turtle
            self.drawer = turtle.RawTurtle(self.screen)
            self.drawer.hideturtle()
            self.drawer.speed(0)
            self.drawer.up()

            self.pointer = turtle.RawTurtle(self.screen)
            self.pointer.shape("triangle")
            # make the triangle a narrow, longer pointer (stretch_wid, stretch_len)
            self.pointer.shapesize(1.2, 8)
            self.pointer.color("red")
            self.pointer.up()
            self.pointer.setheading(90)  # point up at start
            # place the pointer at the center of the wheel
            self.pointer.goto(0, 0)
            self.pointer.showturtle()

            # internal state
            self.names = []
            self.sector_angle = 360
            self.spinning = False

            # allow closing safely
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
                names = [str(i) for i in range(1, n+1)]
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
            # draw outer circle
            self.drawer.goto(0, -RADIUS)
            self.drawer.setheading(0)
            self.drawer.pendown()
            self.drawer.pensize(2)
            self.drawer.circle(RADIUS)
            self.drawer.penup()

            # labels around
            for i, name in enumerate(self.names):
                angle = 90 - (i * self.sector_angle + self.sector_angle / 2)
                rad = math.radians(angle)
                x = math.cos(rad) * (RADIUS - 40)
                y = math.sin(rad) * (RADIUS - 40)
                self.drawer.goto(x, y)
                self.drawer.setheading(angle - 90)
                # draw text using turtle.write (font small) for compatibility
                try:
                    self.drawer.write(name, align="center", font=("Arial", 12, "normal"))
                except Exception:
                    # fallback: use tkinter text on top of canvas
                    self.screen.getcanvas().create_text(CANVAS_SIZE//2 + x, CANVAS_SIZE//2 - y,
                                                       text=name, fill="black", font=("Arial", 12))

            # center mark
            self.drawer.goto(0, 0)
            self.drawer.dot(8, "black")

            # pointer initial position: pointer sits at the center and points up by default
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
            # compute angles: pointer heading 90 means pointing up, map indices so that index 0 is at top sector center
            target_angle = 90 - (target_index * self.sector_angle + self.sector_angle / 2)
            # We'll spin multiple full rotations then land on target_angle
            full_rotations = np.random.randint(3, 7)  # random extra spins
            start_heading = self.pointer.heading()
            # Normalize headings to avoid big jumps
            # We will animate from start_heading to start_heading + total_delta (in degrees)
            # Find minimal delta to reach target after full rotations
            desired_final = start_heading + (full_rotations * 360) + (target_angle - start_heading)
            # animation parameters
            steps = 120
            duration = 3.0  # seconds
            interval = int((duration / steps) * 1000)  # ms per step
            step = 0

            def animate():
                nonlocal step
                if not self.spinning:
                    return
                t = step / steps
                # ease out cubic
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
            # reset pointer and re-create it centered in the wheel
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
            # stop turtle event loop properly and show a farewell message
            try:
                self.spinning = False
                try:
                    self.screen.bye()
                except Exception:
                    pass
                # show a friendly farewell to the user
                try:
                    messagebox.showinfo("提示", "欢迎下次使用！", parent=self.root)
                except Exception:
                    # if messagebox fails for any reason, ignore and continue shutdown
                    pass
            except Exception:
                pass
            try:
                self.root.destroy()
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
                return

            while True:
                b = input("开始抽取请按回车键(输入q退出)：\n")
                if b == "q":
                    print("退出程序。")
                    print("欢迎下次使用！")
                    break
                # 抽取逻辑
                print(f"抽取 {n} 名学生...")
                r = np.random.randint(1, n+1)
                print(f"结果：{r}")
    if __name__ == "__main__":
        # Prefer GUI mode. To force CLI, run: python main_v2.py cli  or pass '2' as arg.
        if len(sys.argv) > 1 and sys.argv[1].lower() in ("2", "cli", "cmd"):
            CmdApp(None)
        else:
            # Use a tiny GUI prompt to choose mode when a console isn't available.
            root = tk.Tk()
            # hide while asking so dialog appears clean
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
                messagebox.showinfo("欢迎使用——dzm", "欢迎使用上课自动抽号系统！\n请在左侧输入学生名单或人数，然后点击“生成轮盘”开始。", parent=root)
                app = PickerApp(root)
                # ensure text input has focus
                try:
                    app.names_text.focus_set()
                except Exception:
                    pass
                root.mainloop()
except Exception as e:
    messagebox.showerror("发生【系统、文件级】错误", f"错误：{e}\n可能发生的【系统、文件级】^错误：\n键盘中断，系统死机、关机，图形界面不可用（如远程终端、服务器），Windows版本过低，等。)\n^:python无法处理此类错误，如果发生请尝试使用【源代码】.py --cython-->>>【源代码】.c")