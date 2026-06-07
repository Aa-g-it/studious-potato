import csv
import logging
import os
import sqlite3
import sys
import time
from datetime import datetime

try:
    import colorama
    from colorama import Fore, Style
except ImportError:
    print("请先安装 colorama: pip install colorama")
    sys.exit(1)

try:
    import colorlog
except ImportError:
    print("请先安装 colorlog: pip install colorlog")
    sys.exit(1)

try:
    import xlwt
except ImportError:
    print("请先安装 xlwt: pip install xlwt")
    sys.exit(1)

try:
    import openpyxl
    from openpyxl import Workbook
except ImportError:
    print("请先安装 openpyxl: pip install openpyxl")
    sys.exit(1)

colorama.init(autoreset=True)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SAVE_DIR = os.path.join(".//data")
LOG_DIR = os.path.join(BASE_DIR, "log")
LOG_FILE = os.path.join(LOG_DIR, datetime.now().strftime("%Y%m%d_students_manage.log"))
CSV_FILE = os.path.join(SAVE_DIR, "data.csv")
DB_FILE = os.path.join(SAVE_DIR, "data.db")
XLS_FILE = os.path.join(SAVE_DIR, "data.xls")
XLSX_FILE = os.path.join(SAVE_DIR, "data.xlsx")
STUDENT_TABLE = "students"
FIELD_NAMES = ["ID", "class", "eduNo", "name", "inschool"]

logger = logging.getLogger(__name__)
file_logger = logging.getLogger(f"{__name__}.file")
UI_MODE = False

SYSTEM_LEVEL = 25
LITTLE_ERROR_LEVEL = 35
MIDDLE_ERROR_LEVEL = 45
MAIN_ERROR_LEVEL = 55
logging.addLevelName(SYSTEM_LEVEL, "SYSTEM")
logging.addLevelName(LITTLE_ERROR_LEVEL, "LITTLEERROR")
logging.addLevelName(MIDDLE_ERROR_LEVEL, "MIDDLEERROR")
logging.addLevelName(MAIN_ERROR_LEVEL, "MAINERROR")


def _logger_system(self, message, *args, **kwargs):
    if self.isEnabledFor(SYSTEM_LEVEL):
        self._log(SYSTEM_LEVEL, message, args, **kwargs)


def _logger_littleerror(self, message, *args, **kwargs):
    if self.isEnabledFor(LITTLE_ERROR_LEVEL):
        self._log(LITTLE_ERROR_LEVEL, message, args, **kwargs)


def _logger_middlerror(self, message, *args, **kwargs):
    if self.isEnabledFor(MIDDLE_ERROR_LEVEL):
        self._log(MIDDLE_ERROR_LEVEL, message, args, **kwargs)


def _logger_mainerror(self, message, *args, **kwargs):
    if self.isEnabledFor(MAIN_ERROR_LEVEL):
        self._log(MAIN_ERROR_LEVEL, message, args, **kwargs)

logging.Logger.system = _logger_system
logging.Logger.littleerror = _logger_littleerror
logging.Logger.middlerror = _logger_middlerror
logging.Logger.mainerror = _logger_mainerror


def init_logging() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    file_logger.setLevel(logging.DEBUG)
    file_logger.handlers.clear()
    file_logger.propagate = False
    file_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)s] %(message)s%(reset)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "SYSTEM": "green",
            "INFO": "yellow",
            "WARNING": "yellow",
            "ERROR": "light_red",
            "CRITICAL": "red",
            "LITTLEERROR": "light_red",
            "MIDDLEERROR": "red",
            "MAINERROR": "purple",
        },
        secondary_log_colors={
            "message": {
                "SYSTEM": "green",
                "INFO": "yellow",
                "WARNING": "yellow",
                "ERROR": "light_red",
                "CRITICAL": "red",
                "LITTLEERROR": "light_red",
                "MIDDLEERROR": "red",
                "MAINERROR": "purple",
            }
        },
        reset=True,
    )
    console_handler.setFormatter(console_formatter)

    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False
    logger.addHandler(console_handler)


def type_prompt(prompt: str, delay: float = 0.01) -> None:
    for char in prompt:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)


def ui_prompt(prompt: str) -> str:
    type_prompt(prompt, 0.01)
    return input("")


def log(message: str, level: str = "INFO"):
    normalized = level.strip().upper()
    log_level = logging.INFO
    if normalized == "SYSTEM":
        log_level = SYSTEM_LEVEL
    elif normalized in {"WARN", "WARNING"}:
        log_level = logging.WARNING
    elif normalized == "LITTLEERROR":
        log_level = LITTLE_ERROR_LEVEL
    elif normalized in {"MIDLEERROR", "MIDDLEERROR"}:
        log_level = MIDDLE_ERROR_LEVEL
    elif normalized == "MAINERROR":
        log_level = MAIN_ERROR_LEVEL
    elif normalized == "ERROR":
        log_level = logging.ERROR

    file_logger.log(log_level, message)
    if UI_MODE:
        ui_prefix = f"[{normalized}] " if normalized != "" else ""
        type_line(f"{ui_prefix}{message}", 0.01)
    else:
        if normalized == "SYSTEM":
            logger.system(message)
        elif normalized in {"WARN", "WARNING"}:
            logger.warning(message)
        elif normalized == "LITTLEERROR":
            logger.littleerror(message)
        elif normalized in {"MIDLEERROR", "MIDDLEERROR"}:
            logger.middlerror(message)
        elif normalized == "MAINERROR":
            logger.mainerror(message)
        elif normalized == "ERROR":
            logger.error(message)
        else:
            logger.info(message)


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")

ui_menu_template = [
    "+------------------------------------------------+",
    "|              STUDENT MANAGEMENT UI             |",
    "+------------------------------------------------+",
    "| 1. 添加学生                                    |",
    "| 2. 编辑学生                                    |",
    "| 3. 查看所有学生                                |",
    "| 4. 导出CSV                                     |",
    "| 5. 导出XLS                                     |",
    "| 6. 导出XLSX                                    |",
    "| 7. 导出所有格式                                |",
    "| 8. 重置数据                                    |",
    "| 9. 帮助                                        |",
    "| 0. 退出                                        |",
    "+------------------------------------------------+",
]


def type_line(text: str, delay: float = 0.02) -> None:
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")
    sys.stdout.flush()


def ui_menu() -> None:
    clear_screen()
    type_line("Mr.Developer> 欢迎使用 STUDENT MANAGEMENT UI", 0.04)
    type_line("Mr.Developer> 正在加载菜单...\n", 0.03)
    for line in ui_menu_template:
        type_line(line, 0.01)
    print()


def ui_mode() -> None:
    global UI_MODE
    UI_MODE = True
    while True:
        ui_menu()
        try:
            choice = ui_prompt("请选择操作 [0-9]：").strip()
        except KeyboardInterrupt:
            print()
            log("已退出 UI 模式。", "SYSTEM")
            break
        if choice == "0":
            break
        if choice == "1":
            add_student()
        elif choice == "2":
            edit_student()
        elif choice == "3":
            show_students()
        elif choice == "4":
            export_csv()
        elif choice == "5":
            export_xls()
        elif choice == "6":
            export_xlsx()
        elif choice == "7":
            export_csv(silent=True)
            export_xls()
            export_xlsx()
            log("已导出所有格式。", "INFO")
        elif choice == "8":
            reset_data()
        elif choice == "9":
            print_help()
        else:
            log("无效选择，请输入 0-9。", "ERROR")
        try:
            ui_prompt("按回车继续...")
        except KeyboardInterrupt:
            print()
            log("已退出 UI 模式。", "SYSTEM")
            break
    UI_MODE = False


def init_db() -> None:
    os.makedirs(SAVE_DIR, exist_ok=True)
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {STUDENT_TABLE} (
                ID INTEGER PRIMARY KEY,
                class TEXT,
                eduNo INTEGER,
                name TEXT,
                inschool TEXT
            )
        """)
        conn.commit()
    if not os.path.exists(CSV_FILE):
        export_csv()
    log("数据库初始化完成。", "SYSTEM")


def load_students() -> list[tuple]:
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute(
            f"SELECT ID, class, eduNo, name, inschool FROM {STUDENT_TABLE} ORDER BY ID"
        )
        return cursor.fetchall()


def sync_csv() -> None:
    export_csv(silent=True)


def export_csv(silent: bool = False) -> str:
    rows = load_students()
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(FIELD_NAMES)
        writer.writerows(rows)
    if not silent:
        log(f"已导出 CSV：{CSV_FILE}", "INFO")
    return CSV_FILE


def export_xls() -> str:
    rows = load_students()
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("Students")
    for col_index, header in enumerate(FIELD_NAMES):
        sheet.write(0, col_index, header)
    for row_index, row in enumerate(rows, start=1):
        for col_index, value in enumerate(row):
            sheet.write(row_index, col_index, value)
    workbook.save(XLS_FILE)
    log(f"已导出 XLS：{XLS_FILE}", "INFO")
    return XLS_FILE


def export_xlsx() -> str:
    rows = load_students()
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Students"
    sheet.append(FIELD_NAMES)
    for row in rows:
        sheet.append(row)
    workbook.save(XLSX_FILE)
    log(f"已导出 XLSX：{XLSX_FILE}", "INFO")
    return XLSX_FILE


def show_students() -> None:
    rows = load_students()
    if not rows:
        log("当前无学生记录。", "WARN")
        return
    line = ",".join(FIELD_NAMES)
    if UI_MODE:
        type_line(line, 0.005)
    else:
        print(line)
    for row in rows:
        row_line = ",".join(str(value) for value in row)
        if UI_MODE:
            type_line(row_line, 0.005)
        else:
            print(row_line)
    log(f"共 {len(rows)} 条记录。", "INFO")


def get_student(student_id: int) -> tuple | None:
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute(
            f"SELECT ID, class, eduNo, name, inschool FROM {STUDENT_TABLE} WHERE ID = ?",
            (student_id,),
        )
        return cursor.fetchone()


def add_student() -> None:
    try:
        student_id = int(input("请输入学生 ID：").strip())
    except ValueError:
        log("ID 必须是整数。", "ERROR")
        return
    existing = get_student(student_id)
    if existing:
        log(f"ID={student_id} 的学生已存在，请使用 edit 命令编辑。", "WARN")
        return
    class_name = input("请输入班级：").strip()
    try:
        edu_no = int(input("请输入学号：").strip())
    except ValueError:
        log("学号必须是整数。", "ERROR")
        return
    name = input("请输入姓名：").strip()
    in_school = input("是否在校 (T/F)：").strip().upper() or "T"
    in_school = "T" if in_school.startswith("T") else "F"
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            f"INSERT INTO {STUDENT_TABLE} (ID, class, eduNo, name, inschool) VALUES (?, ?, ?, ?, ?)",
            (student_id, class_name, edu_no, name, in_school),
        )
        conn.commit()
    sync_csv()
    log(f"新增学生：ID={student_id}，姓名={name}。", "INFO")


def edit_student() -> None:
    try:
        student_id = int(input("请输入要编辑的学生 ID：").strip())
    except ValueError:
        log("ID 必须是整数。", "ERROR")
        return
    student = get_student(student_id)
    if not student:
        log(f"未找到 ID={student_id} 的学生。", "ERROR")
        return
    _, current_class, current_edu_no, current_name, current_inschool = student
    print(f"当前班级：{current_class}")
    class_name = input("新的班级（回车保持不变）：").strip() or current_class
    print(f"当前学号：{current_edu_no}")
    edu_input = input("新的学号（回车保持不变）：").strip()
    try:
        edu_no = int(edu_input) if edu_input else current_edu_no
    except ValueError:
        log("学号必须是整数。", "ERROR")
        return
    print(f"当前姓名：{current_name}")
    name = input("新的姓名（回车保持不变）：").strip() or current_name
    print(f"当前在校状态：{current_inschool}")
    in_school_input = input("新的在校状态 (T/F，回车保持不变)：").strip().upper()
    in_school = current_inschool if not in_school_input else ("T" if in_school_input.startswith("T") else "F")
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            f"UPDATE {STUDENT_TABLE} SET class = ?, eduNo = ?, name = ?, inschool = ? WHERE ID = ?",
            (class_name, edu_no, name, in_school, student_id),
        )
        conn.commit()
    sync_csv()
    log(f"已更新学生 ID={student_id}。", "INFO")


def reset_data() -> None:
    confirm = input("确认清除所有学生数据？输入 YES 确认：").strip().upper()
    if confirm != "YES":
        log("重置已取消。", "WARN")
        return
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(f"DELETE FROM {STUDENT_TABLE}")
        conn.commit()
    export_csv(silent=True)
    log("已清除所有学生数据。", "INFO")


def print_help() -> None:
    lines = [
        "可用命令：",
        "  add           - 添加学生",
        "  edit          - 编辑现有学生",
        "  view          - 查看所有学生（SQL 输出）",
        "  sql           - 查看所有学生（SQL 输出）",
        "  reset         - 归零，清空所有学生数据",
        "  export csv    - 导出 CSV",
        "  export xls    - 导出 XLS",
        "  export xlsx   - 导出 XLSX",
        "  export all    - 同时导出 CSV、XLS、XLSX",
        "  ui            - 进入 MS-DOS 样式折叠视图 UI",
        "  help          - 显示此帮助",
        "  exit          - 退出程序",
    ]
    for line in lines:
        if UI_MODE:
            type_line(line, 0.01)
        else:
            print(line)


def parse_command(command: str) -> tuple[str, list[str]]:
    parts = command.strip().split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]


def main() -> None:
    init_logging()
    init_db()
    log("输入 help 查看命令。", "SYSTEM")
    while True:
        try:
            command_line = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not command_line:
            continue
        command, args = parse_command(command_line)
        if command in {"exit", "quit"}:
            break
        if command == "help":
            print_help()
        elif command == "add":
            add_student()
        elif command == "edit":
            edit_student()
        elif command in {"view", "sql"}:
            show_students()
        elif command == "ui":
            ui_mode()
        elif command == "reset":
            reset_data()
        elif command == "export":
            if not args:
                log("请指定导出类型：csv、xls、xlsx 或 all。", "ERROR")
                continue
            choice = args[0].lower()
            if choice == "csv":
                export_csv()
            elif choice == "xls":
                export_xls()
            elif choice == "xlsx":
                export_xlsx()
            elif choice == "all":
                export_csv(silent=True)
                export_xls()
                export_xlsx()
                log("已导出所有格式。", "INFO")
            else:
                log("未知导出类型，请使用 csv、xls、xlsx 或 all。", "ERROR")
        else:
            log("未知命令，请输入 help 查看可用命令。", "ERROR")
    log("程序已退出。", "SYSTEM")


if __name__ == "__main__":
    main()
