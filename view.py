import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, List, Any, Optional

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator

class PatientFormDialog(tk.Toplevel):
    """Вертикальная форма для добавления и редактирования пациента."""

    def __init__(
        self,
        parent: tk.Tk,
        title: str,
        genders: tuple,
        on_submit: Callable[[str, str, str, str, str, str, str], bool],
        initial_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_submit = on_submit
        self.genders = genders

        container = ttk.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        self.last_name_var = tk.StringVar(
            value=initial_data["last_name"] if initial_data else ""
        )
        self.first_name_var = tk.StringVar(
            value=initial_data["first_name"] if initial_data else ""
        )
        self.middle_name_var = tk.StringVar(
            value=initial_data["middle_name"] if initial_data else ""
        )
        self.age_var = tk.StringVar(
            value=str(initial_data["age"]) if initial_data else ""
        )
        self.gender_var = tk.StringVar(
            value=initial_data["gender"] if initial_data else genders[0]
        )
        self.height_var = tk.StringVar(
            value=str(initial_data["height"]) if initial_data else ""
        )
        self.weight_var = tk.StringVar(
            value=str(initial_data["weight"]) if initial_data else ""
        )

        # Вертикальная форма: названия с большой буквы над полями ввода
        self._create_field(container, "Фамилия", self.last_name_var)
        self._create_field(container, "Имя", self.first_name_var)
        self._create_field(container, "Отчество", self.middle_name_var)
        self._create_field(container, "Возраст", self.age_var)

        ttk.Label(container, text="Пол").pack(anchor="w", pady=(8, 2))
        gender_combo = ttk.Combobox(
            container,
            textvariable=self.gender_var,
            values=self.genders,
            state="readonly",
            width=32,
        )
        gender_combo.pack(fill="x", pady=(0, 6))

        self._create_field(container, "Рост (см)", self.height_var)
        self._create_field(container, "Вес (кг)", self.weight_var)

        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill="x", pady=(14, 0))

        ttk.Button(btn_frame, text="Сохранить", command=self._submit).pack(
            side="left", expand=True, fill="x", padx=(0, 5)
        )
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(
            side="left", expand=True, fill="x", padx=(5, 0)
        )

        self.bind("<Return>", lambda _: self._submit())
        self.bind("<Escape>", lambda _: self.destroy())

    @staticmethod
    def _create_field(parent: ttk.Frame, label_text: str, var: tk.StringVar) -> None:
        ttk.Label(parent, text=label_text).pack(anchor="w", pady=(8, 2))
        ttk.Entry(parent, textvariable=var, width=35).pack(fill="x", pady=(0, 6))

    def _submit(self) -> None:
        success = self.on_submit(
            self.last_name_var.get(),
            self.first_name_var.get(),
            self.middle_name_var.get(),
            self.age_var.get(),
            self.gender_var.get(),
            self.height_var.get(),
            self.weight_var.get(),
        )
        if success:
            self.destroy()

class StatsWindow(tk.Toplevel):
    """Окно со сводной статистикой (4 графика)."""

    def __init__(self, parent: tk.Tk, patients: List[Dict[str, Any]], genders: tuple):
        super().__init__(parent)
        self.title("Сводная статистика")
        self.geometry("1050x750")
        self.transient(parent)

        fig = Figure(figsize=(10, 7), dpi=100)
        fig.subplots_adjust(hspace=0.4, wspace=0.3)

        ax1 = fig.add_subplot(2, 2, 1)
        ax2 = fig.add_subplot(2, 2, 2)
        ax3 = fig.add_subplot(2, 2, 3)
        ax4 = fig.add_subplot(2, 2, 4)

        # 1. Распределение пациентов по полу
        gender_counts = [
            sum(1 for p in patients if p["gender"] == g) for g in genders
        ]
        ax1.bar(
            genders,
            gender_counts,
            color=["#4A90E2", "#E26A8D", "#9B9B9B"],
            edgecolor="black",
        )
        ax1.set_title("Распределение пациентов по полу")
        ax1.set_ylabel("Количество пациентов")
        ax1.yaxis.set_major_locator(MaxNLocator(integer=True))

        # 2. Распределение пациентов по возрасту
        ages = [p["age"] for p in patients]
        ax2.hist(ages, bins="auto", color="#50B89C", edgecolor="black")
        ax2.set_title("Распределение пациентов по возрасту")
        ax2.set_xlabel("Возраст (лет)")
        ax2.set_ylabel("Количество пациентов")
        ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

        # 3. Распределение ИМТ с учётом пола
        bmi_by_gender = []
        present_genders = []
        for g in genders:
            bmis = [p["bmi"] for p in patients if p["gender"] == g]
            if bmis:
                bmi_by_gender.append(bmis)
                present_genders.append(g)

        if bmi_by_gender:
            ax3.boxplot(bmi_by_gender)
            ax3.set_xticks(range(1, len(present_genders) + 1))
            ax3.set_xticklabels(present_genders)
        ax3.set_title("Распределение ИМТ с учётом пола")
        ax3.set_ylabel("ИМТ")

        # 4. Зависимость ИМТ от возраста
        colors = {"мужской": "#4A90E2", "женский": "#E26A8D", "неопределенный": "#777777"}
        for g in genders:
            g_patients = [p for p in patients if p["gender"] == g]
            if g_patients:
                ax4.scatter(
                    [p["age"] for p in g_patients],
                    [p["bmi"] for p in g_patients],
                    label=g,
                    color=colors.get(g, "#333333"),
                    alpha=0.85,
                    edgecolors="black",
                )
        ax4.axhline(16.0, color="#D32F2F", linestyle="--", alpha=0.5, label="Граница опасного ИМТ (16 / 30)")
        ax4.axhline(30.0, color="#D32F2F", linestyle="--", alpha=0.5)
        ax4.set_title("Зависимость ИМТ от возраста")
        ax4.set_xlabel("Возраст (лет)")
        ax4.set_ylabel("ИМТ")
        ax4.legend(fontsize=8)
        ax4.grid(True, linestyle="--", alpha=0.4)

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

class PatientView:
    """Главное окно приложения."""

    def __init__(self, genders: tuple):
        self.root = tk.Tk()
        self.root.title("Учёт пациентов")
        self.root.geometry("940x550")
        self.genders = genders

        self.on_add_click: Optional[Callable[[], None]] = None
        self.on_edit_click: Optional[Callable[[str], None]] = None
        self.on_delete_click: Optional[Callable[[str], None]] = None
        self.on_stats_click: Optional[Callable[[], None]] = None

        self._configure_treeview_tags_fix()
        self._build_ui()

    @staticmethod
    def _configure_treeview_tags_fix() -> None:
        """Исправление для корректного отображения цветов тегов в Treeview на Tk 8.6+."""
        style = ttk.Style()

        def fixed_map(option: str):
            return [
                elm
                for elm in style.map("Treeview", query_opt=option)
                if elm[:2] != ("!disabled", "!selected")
            ]

        style.map(
            "Treeview",
            foreground=fixed_map("foreground"),
            background=fixed_map("background"),
        )

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill="both", expand=True)

        # Панель кнопок сверху
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(
            btn_frame,
            text="Добавить пациента",
            command=lambda: self.on_add_click and self.on_add_click(),
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            btn_frame,
            text="Редактировать пациента",
            command=self._handle_edit,
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            btn_frame,
            text="Удалить пациента",
            command=self._handle_delete,
        ).pack(side="left", padx=(0, 6))

        ttk.Button(
            btn_frame,
            text="Сводная статистика",
            command=lambda: self.on_stats_click and self.on_stats_click(),
        ).pack(side="right")

        # Таблица пациентов
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill="both", expand=True)

        columns = ("fio", "age", "gender", "height", "weight", "bmi")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse"
        )

        headings = {
            "fio": ("ФИО", 270),
            "age": ("Возраст", 80),
            "gender": ("Пол", 130),
            "height": ("Рост (см)", 100),
            "weight": ("Вес (кг)", 100),
            "bmi": ("ИМТ", 90),
        }
        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text)
            anchor = "w" if col == "fio" else "center"
            self.tree.column(col, width=width, anchor=anchor)

        # Настройка подсветки ИМТ
        self.tree.tag_configure("danger", background="#FFCDD2", foreground="#B71C1C")
        self.tree.tag_configure("warning", background="#FFF3CD", foreground="#856404")

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Легенда подсветки под таблицей
        legend_frame = ttk.Frame(main_frame)
        legend_frame.pack(fill="x", pady=(8, 0))

        tk.Label(
            legend_frame,
            text="  Опасный ИМТ (< 16 или ≥ 30)  ",
            bg="#FFCDD2",
            fg="#B71C1C",
            relief="solid",
            bd=1,
        ).pack(side="left", padx=(0, 10))

        tk.Label(
            legend_frame,
            text="  Отклонение от нормы (16–18.49 или 25–29.99)  ",
            bg="#FFF3CD",
            fg="#856404",
            relief="solid",
            bd=1,
        ).pack(side="left", padx=(0, 10))

        ttk.Label(legend_frame, text="Норма: 18.5–24.99").pack(side="left")

    def _get_selected_id(self) -> Optional[str]:
        selected = self.tree.selection()
        if not selected:
            return None
        return selected[0]

    def _handle_edit(self) -> None:
        patient_id = self._get_selected_id()
        if not patient_id:
            self.show_warning("Внимание", "Выберите пациента в таблице для редактирования.")
            return
        if self.on_edit_click:
            self.on_edit_click(patient_id)

    def _handle_delete(self) -> None:
        patient_id = self._get_selected_id()
        if not patient_id:
            self.show_warning("Внимание", "Выберите пациента в таблице для удаления.")
            return
        if self.on_delete_click:
            self.on_delete_click(patient_id)

    def update_table(self, patients: List[Dict[str, Any]]) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for p in patients:
            status = p.get("bmi_status", "normal")
            tags = (status,) if status in ("danger", "warning") else ()
            self.tree.insert(
                "",
                "end",
                iid=p["id"],
                values=(
                    p["fio"],
                    p["age"],
                    p["gender"],
                    p["height"],
                    p["weight"],
                    p["bmi"],
                ),
                tags=tags,
            )

    def open_patient_form(
        self,
        title: str,
        on_submit: Callable[[str, str, str, str, str, str, str], bool],
        initial_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        PatientFormDialog(
            self.root, title, self.genders, on_submit, initial_data=initial_data
        )

    def open_stats_window(self, patients: List[Dict[str, Any]]) -> None:
        StatsWindow(self.root, patients, self.genders)

    def show_error(self, title: str, message: str) -> None:
        messagebox.showerror(title, message, parent=self.root)

    def show_warning(self, title: str, message: str) -> None:
        messagebox.showwarning(title, message, parent=self.root)

    def ask_confirm(self, title: str, message: str) -> bool:
        return messagebox.askyesno(title, message, parent=self.root)

    def run(self) -> None:
        self.root.mainloop()