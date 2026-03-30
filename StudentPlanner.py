import json
import uuid
from copy import deepcopy
from datetime import date, datetime, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk


APP_DIR = Path(__file__).resolve().parent
DATA_PATH = APP_DIR / "data" / "student_dashboard_data.json"

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

DAY_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
PRIORITY_ORDER = {"Urgent": 0, "High": 1, "Medium": 2, "Low": 3}

BG = "#0f0d12"
SIDEBAR = "#141219"
PANEL = "#1b1820"
PANEL_ALT = "#241f2a"
TEXT = "#f5efe3"
MUTED = "#b9ad97"
GOLD = "#c39b57"
GOLD_SOFT = "#e0c17e"
RED = "#d16c62"
GREEN = "#6e966a"
BLUE = "#607f93"
PURPLE_GREY = "#665c76"
OUTLINE = "#3f364b"

SUBJECT_COLORS = [
    "#71573e",
    "#8a5d4d",
    "#5f7256",
    "#536f80",
    "#756580",
    "#8a6e45",
    "#5a6a7b",
    "#7d5b63",
]

QUOTES = [
    "Discipline is the quiet bridge between your plans and your results.",
    "Small study sessions, repeated with care, become big achievements.",
    "You do not need perfect days. You need steady ones.",
    "Progress grows when intention meets routine.",
    "Every focused hour is a vote for the future you want.",
    "Consistency often looks ordinary while it is building something extraordinary.",
]


def make_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def create_default_data():
    today = date.today()
    return {
        "tasks": [
            {
                "id": make_id("task"),
                "title": "Finish Python assignment",
                "priority": "Urgent",
                "done": False,
            },
            {
                "id": make_id("task"),
                "title": "Revise database chapter 3",
                "priority": "High",
                "done": False,
            },
            {
                "id": make_id("task"),
                "title": "Organize lecture notes",
                "priority": "Medium",
                "done": True,
            },
        ],
        "exams": [
            {
                "id": make_id("exam"),
                "subject": "Algorithms",
                "date": (today + timedelta(days=3)).isoformat(),
                "time": "10:00",
                "hall": "Hall A2",
            },
            {
                "id": make_id("exam"),
                "subject": "Statistics",
                "date": (today + timedelta(days=10)).isoformat(),
                "time": "13:30",
                "hall": "Hall B1",
            },
        ],
        "timetable": [
            {
                "id": make_id("slot"),
                "day": "Sunday",
                "time": "09:00 - 10:30",
                "subject": "Python Lab",
                "room": "Lab 4",
            },
            {
                "id": make_id("slot"),
                "day": "Monday",
                "time": "11:00 - 12:30",
                "subject": "Algorithms",
                "room": "Room 214",
            },
            {
                "id": make_id("slot"),
                "day": "Tuesday",
                "time": "12:00 - 13:30",
                "subject": "Databases",
                "room": "Room 310",
            },
            {
                "id": make_id("slot"),
                "day": "Wednesday",
                "time": "09:30 - 11:00",
                "subject": "Statistics",
                "room": "Room 105",
            },
            {
                "id": make_id("slot"),
                "day": "Thursday",
                "time": "14:00 - 15:30",
                "subject": "Software Engineering",
                "room": "Room 122",
            },
        ],
        "grades": [
            {"id": make_id("grade"), "subject": "Algorithms", "score": 84},
            {"id": make_id("grade"), "subject": "Databases", "score": 76},
            {"id": make_id("grade"), "subject": "Python Lab", "score": 92},
            {"id": make_id("grade"), "subject": "Statistics", "score": 69},
        ],
        "timer_settings": {"work_minutes": 25, "break_minutes": 5},
        "habits": [
            {"id": make_id("habit"), "name": "Study 2 hours", "week": [1, 1, 0, 1, 0, 0, 0]},
            {"id": make_id("habit"), "name": "Review notes", "week": [1, 0, 1, 1, 0, 0, 0]},
            {"id": make_id("habit"), "name": "Sleep before midnight", "week": [0, 1, 1, 0, 0, 0, 0]},
        ],
        "notes": "Use this space for summaries, reminders, and quick ideas.",
    }


def merge_defaults(default_value, loaded_value):
    if isinstance(default_value, dict):
        merged = {}
        loaded_value = loaded_value if isinstance(loaded_value, dict) else {}
        for key, value in default_value.items():
            merged[key] = merge_defaults(value, loaded_value.get(key))
        for key, value in loaded_value.items():
            if key not in merged:
                merged[key] = value
        return merged
    if isinstance(default_value, list):
        return loaded_value if isinstance(loaded_value, list) else deepcopy(default_value)
    return loaded_value if loaded_value is not None else default_value


class DataStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self):
        defaults = create_default_data()
        if not self.path.exists():
            self.save(defaults)
            return defaults

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return merge_defaults(defaults, data)
        except (OSError, json.JSONDecodeError):
            self.save(defaults)
            return defaults

    def save(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, bg_color):
        super().__init__(parent, bg=bg_color)
        self.canvas = tk.Canvas(
            self,
            bg=bg_color,
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        self.scrollbar = tk.Canvas(
            self,
            width=18,
            bg=PANEL,
            highlightthickness=0,
            bd=0,
            relief="flat",
            cursor="hand2",
        )
        self.content = tk.Frame(self.canvas, bg=bg_color)
        self.window_id = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.canvas.configure(yscrollcommand=self._sync_scrollbar)
        self.scroll_first = 0.0
        self.scroll_last = 1.0
        self.scroll_thumb = None
        self.thumb_bounds = (3, 3, 15, 45)
        self.drag_offset = 0

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y", padx=(6, 0))

        self.content.bind("<Configure>", self._update_scrollregion)
        self.canvas.bind("<Configure>", self._resize_window)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)
        self.content.bind("<Enter>", self._bind_mousewheel)
        self.content.bind("<Leave>", self._unbind_mousewheel)
        self.scrollbar.bind("<Configure>", self._draw_scrollbar)
        self.scrollbar.bind("<Button-1>", self._start_scroll_drag)
        self.scrollbar.bind("<B1-Motion>", self._drag_scroll_thumb)

    def _update_scrollregion(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_window(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _bind_mousewheel(self, _event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)

    def _unbind_mousewheel(self, _event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        direction = -1 if getattr(event, "num", None) == 4 else 1
        self.canvas.yview_scroll(direction, "units")

    def _sync_scrollbar(self, first, last):
        self.scroll_first = float(first)
        self.scroll_last = float(last)
        self._draw_scrollbar()

    def _draw_scrollbar(self, _event=None):
        canvas = self.scrollbar
        canvas.delete("all")

        width = max(canvas.winfo_width(), 18)
        height = max(canvas.winfo_height(), 10)
        track_x0 = 4
        track_x1 = width - 4
        track_y0 = 4
        track_y1 = height - 4

        canvas.create_rectangle(
            track_x0,
            track_y0,
            track_x1,
            track_y1,
            fill=PANEL_ALT,
            outline=OUTLINE,
            width=1,
        )

        visible_fraction = self.scroll_last - self.scroll_first
        thumb_height = max(42, visible_fraction * (track_y1 - track_y0))
        thumb_height = min(thumb_height, track_y1 - track_y0)

        max_top = track_y1 - thumb_height
        thumb_top = track_y0 + (self.scroll_first * max(0, max_top - track_y0))
        thumb_bottom = thumb_top + thumb_height

        if visible_fraction >= 0.999:
            thumb_top = track_y0
            thumb_bottom = track_y1

        self.thumb_bounds = (track_x0 + 2, thumb_top, track_x1 - 2, thumb_bottom)
        canvas.create_rectangle(
            self.thumb_bounds[0],
            self.thumb_bounds[1],
            self.thumb_bounds[2],
            self.thumb_bounds[3],
            fill=GOLD,
            outline=GOLD_SOFT,
            width=1,
        )

    def _start_scroll_drag(self, event):
        x0, y0, x1, y1 = self.thumb_bounds
        if x0 <= event.x <= x1 and y0 <= event.y <= y1:
            self.drag_offset = event.y - y0
            return

        thumb_height = y1 - y0
        self.drag_offset = thumb_height / 2
        self._move_thumb(event.y - self.drag_offset)

    def _drag_scroll_thumb(self, event):
        self._move_thumb(event.y - self.drag_offset)

    def _move_thumb(self, thumb_top):
        track_top = 4
        track_bottom = max(self.scrollbar.winfo_height() - 4, track_top + 1)
        thumb_height = self.thumb_bounds[3] - self.thumb_bounds[1]
        travel = (track_bottom - track_top) - thumb_height
        visible_fraction = self.scroll_last - self.scroll_first

        if travel <= 0 or visible_fraction >= 0.999:
            self.canvas.yview_moveto(0)
            return

        clamped_top = min(max(thumb_top, track_top), track_bottom - thumb_height)
        fraction = (clamped_top - track_top) / travel
        self.canvas.yview_moveto(fraction * (1 - visible_fraction))


class StudentPlannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Planner")
        self.geometry("1460x900")
        self.minsize(1100, 680)
        self.configure(bg=BG)

        self.store = DataStore(DATA_PATH)
        self.data = self.store.load()
        self.views = {}
        self.nav_buttons = {}
        self.current_view = None
        self.note_save_job = None
        self.timer_job = None

        self.section_order = [
            "Dashboard",
            "To-Do List",
            "Exam Schedule",
            "Timetable",
            "Study Timer",
            "Habit Tracker",
            "Notes",
        ]

        self._configure_fonts()
        self._configure_styles()
        self._setup_timer_state()
        self._build_shell()
        self._build_dashboard_view()
        self._build_tasks_view()
        self._build_exams_view()
        self._build_timetable_view()
        self._build_timer_view()
        self._build_habits_view()
        self._build_notes_view()
        self._refresh_all()
        self.show_view("Dashboard")

        self.after(60000, self._refresh_time_sensitive_sections)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _configure_fonts(self):
        available = set(tkfont.families())

        def pick_font(preferred, fallbacks):
            for family in [preferred] + list(fallbacks):
                if family in available:
                    return family
            return "Segoe UI"

        self.serif_font = pick_font(
            "Playfair Display",
            ["Georgia", "Garamond", "Palatino Linotype", "Times New Roman"],
        )
        self.sans_font = pick_font(
            "Aptos",
            ["Segoe UI", "Verdana", "Arial"],
        )

        self.font_title = (self.serif_font, 28, "bold")
        self.font_subtitle = (self.sans_font, 11)
        self.font_heading = (self.serif_font, 18, "bold")
        self.font_body = (self.sans_font, 11)
        self.font_small = (self.sans_font, 10)
        self.font_metric = (self.serif_font, 24, "bold")
        self.font_metric_small = (self.serif_font, 16, "bold")
        self.font_button = (self.sans_font, 10, "bold")

        self.font_body_strike = tkfont.Font(family=self.sans_font, size=11)
        self.font_body_strike.configure(overstrike=1)

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "DarkAcademic.TCombobox",
            fieldbackground=PANEL_ALT,
            background=PANEL_ALT,
            foreground=TEXT,
            arrowcolor=TEXT,
            bordercolor=OUTLINE,
            lightcolor=OUTLINE,
            darkcolor=OUTLINE,
            insertcolor=TEXT,
        )
        style.map(
            "DarkAcademic.TCombobox",
            fieldbackground=[("readonly", PANEL_ALT)],
            background=[("readonly", PANEL_ALT)],
            foreground=[("readonly", TEXT)],
        )
        style.configure(
            "Dark.Horizontal.TProgressbar",
            troughcolor=PANEL_ALT,
            background=GOLD,
            bordercolor=PANEL_ALT,
            lightcolor=GOLD,
            darkcolor=GOLD,
        )

    def _setup_timer_state(self):
        settings = self.data.get("timer_settings", {})
        self.timer_mode = "work"
        self.timer_running = False
        self.work_minutes_var = tk.StringVar(value=str(settings.get("work_minutes", 25)))
        self.break_minutes_var = tk.StringVar(value=str(settings.get("break_minutes", 5)))
        self.timer_total_seconds = self._current_mode_minutes() * 60
        self.timer_remaining_seconds = self.timer_total_seconds
        self.timer_status_text = "Work mode ready."

    def _build_shell(self):
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=320)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand_frame = tk.Frame(self.sidebar, bg=SIDEBAR)
        brand_frame.pack(fill="x", padx=24, pady=(28, 18))

        self.font_brand = (self.sans_font, 21, "bold")

        tk.Label(
            brand_frame,
            text="Student\nPlanner",
            bg=SIDEBAR,
            fg=TEXT,
            font=self.font_brand,
            wraplength=220,
            justify="left",
        ).pack(anchor="w", fill="x")
        tk.Label(
            brand_frame,
            text="Dark Academic Student Planner",
            bg=SIDEBAR,
            fg=MUTED,
            font=self.font_subtitle,
        ).pack(anchor="w", pady=(6, 0))

        self.today_label = tk.Label(
            brand_frame,
            bg=SIDEBAR,
            fg=GOLD_SOFT,
            font=self.font_small,
        )
        self.today_label.pack(anchor="w", pady=(14, 0))

        nav_frame = tk.Frame(self.sidebar, bg=SIDEBAR)
        nav_frame.pack(fill="x", padx=18, pady=(8, 0))

        for section in self.section_order:
            button = tk.Button(
                nav_frame,
                text=section,
                font=self.font_button,
                bg=SIDEBAR,
                fg=TEXT,
                activebackground=PANEL_ALT,
                activeforeground=TEXT,
                bd=0,
                relief="flat",
                anchor="w",
                padx=16,
                pady=12,
                highlightthickness=0,
                command=lambda name=section: self.show_view(name),
                cursor="hand2",
            )
            button.pack(fill="x", pady=5)
            self.nav_buttons[section] = button

        footer = tk.Frame(self.sidebar, bg=SIDEBAR)
        footer.pack(side="bottom", fill="x", padx=24, pady=24)
        tk.Label(
            footer,
            text="Built with Python + tkinter",
            bg=SIDEBAR,
            fg=MUTED,
            font=self.font_small,
        ).pack(anchor="w")
        tk.Label(
            footer,
            text="Local JSON autosave enabled",
            bg=SIDEBAR,
            fg=MUTED,
            font=self.font_small,
        ).pack(anchor="w", pady=(4, 0))

        self.page_container = tk.Frame(self, bg=BG)
        self.page_container.pack(side="left", fill="both", expand=True)

        self._update_today_label()

    def _create_page(self, title, subtitle):
        page = tk.Frame(self.page_container, bg=BG)
        header = tk.Frame(page, bg=BG)
        header.pack(fill="x", padx=26, pady=(26, 10))

        tk.Label(header, text=title, bg=BG, fg=TEXT, font=self.font_title).pack(anchor="w")
        tk.Label(header, text=subtitle, bg=BG, fg=MUTED, font=self.font_subtitle).pack(anchor="w", pady=(4, 0))

        body = tk.Frame(page, bg=BG)
        body.pack(fill="both", expand=True, padx=26, pady=(0, 26))
        return page, body

    def _make_card(self, parent):
        return tk.Frame(
            parent,
            bg=PANEL,
            highlightbackground=OUTLINE,
            highlightthickness=1,
            bd=0,
        )

    def _build_dashboard_view(self):
        page, body = self._create_page(
            "Dashboard",
            "A quick overview of workload, performance, and your next academic milestone.",
        )
        self.views["Dashboard"] = page

        stats_frame = tk.Frame(body, bg=BG)
        stats_frame.pack(fill="x", pady=(0, 18))
        for column in range(4):
            stats_frame.columnconfigure(column, weight=1)

        self.dashboard_stats = {}
        cards = [
            ("Pending Tasks", "tasks"),
            ("Completion Rate", "progress"),
            ("Habit Rate", "habits"),
            ("Next Exam", "exam"),
        ]
        for index, (label, key) in enumerate(cards):
            card = self._make_card(stats_frame)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 6, 6 if index < 3 else 0))
            tk.Label(card, text=label, bg=PANEL, fg=MUTED, font=self.font_small).pack(anchor="w", padx=18, pady=(16, 4))
            value = tk.Label(card, text="0", bg=PANEL, fg=TEXT, font=self.font_metric)
            value.pack(anchor="w", padx=18)
            caption = tk.Label(card, text="", bg=PANEL, fg=GOLD_SOFT, font=self.font_small, wraplength=240, justify="left")
            caption.pack(anchor="w", padx=18, pady=(6, 16))
            self.dashboard_stats[key] = (value, caption)

        lower_frame = tk.Frame(body, bg=BG)
        lower_frame.pack(fill="both", expand=True)
        lower_frame.columnconfigure(0, weight=1)
        lower_frame.columnconfigure(1, weight=1)
        lower_frame.columnconfigure(2, weight=1)

        tasks_card = self._make_card(lower_frame)
        tasks_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        tk.Label(tasks_card, text="Priority Tasks", bg=PANEL, fg=TEXT, font=self.font_heading).pack(anchor="w", padx=18, pady=(16, 8))
        self.dashboard_task_preview = tk.Frame(tasks_card, bg=PANEL)
        self.dashboard_task_preview.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        exams_card = self._make_card(lower_frame)
        exams_card.grid(row=0, column=1, sticky="nsew", padx=4)
        tk.Label(exams_card, text="Upcoming Exams", bg=PANEL, fg=TEXT, font=self.font_heading).pack(anchor="w", padx=18, pady=(16, 8))
        self.dashboard_exam_preview = tk.Frame(exams_card, bg=PANEL)
        self.dashboard_exam_preview.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        quote_card = self._make_card(lower_frame)
        quote_card.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        tk.Label(quote_card, text="Daily Quote", bg=PANEL, fg=TEXT, font=self.font_heading).pack(anchor="w", padx=18, pady=(16, 8))
        self.dashboard_quote_label = tk.Label(
            quote_card,
            bg=PANEL,
            fg=GOLD_SOFT,
            font=self.font_heading,
            wraplength=330,
            justify="left",
        )
        self.dashboard_quote_label.pack(anchor="w", padx=18, pady=(0, 16))
        self.dashboard_quote_hint = tk.Label(
            quote_card,
            text="Let your routine carry you on days motivation feels quiet.",
            bg=PANEL,
            fg=MUTED,
            font=self.font_small,
            wraplength=330,
            justify="left",
        )
        self.dashboard_quote_hint.pack(anchor="w", padx=18, pady=(0, 18))

    def _build_tasks_view(self):
        page, body = self._create_page(
            "To-Do List",
            "Capture tasks, prioritize them, and keep the study momentum visible.",
        )
        self.views["To-Do List"] = page

        form_card = self._make_card(body)
        form_card.pack(fill="x", pady=(0, 16))

        form_inner = tk.Frame(form_card, bg=PANEL)
        form_inner.pack(fill="x", padx=18, pady=18)
        form_inner.columnconfigure(0, weight=1)

        self.task_title_var = tk.StringVar()
        self.task_priority_var = tk.StringVar(value="High")

        tk.Label(form_inner, text="Task Title", bg=PANEL, fg=MUTED, font=self.font_small).grid(row=0, column=0, sticky="w")
        tk.Label(form_inner, text="Priority", bg=PANEL, fg=MUTED, font=self.font_small).grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.task_entry = tk.Entry(
            form_inner,
            textvariable=self.task_title_var,
            bg=PANEL_ALT,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=self.font_body,
        )
        self.task_entry.grid(row=1, column=0, sticky="ew", pady=(6, 0), ipady=8)
        self.task_entry.bind("<Return>", lambda _event: self.add_task())

        self.task_priority_box = ttk.Combobox(
            form_inner,
            values=list(PRIORITY_ORDER.keys()),
            textvariable=self.task_priority_var,
            state="readonly",
            style="DarkAcademic.TCombobox",
            font=self.font_body,
        )
        self.task_priority_box.grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(6, 0))

        self._make_action_button(form_inner, "Add Task", self.add_task).grid(row=1, column=2, padx=(12, 0), pady=(6, 0))

        progress_card = self._make_card(body)
        progress_card.pack(fill="x", pady=(0, 16))
        tk.Label(progress_card, text="Task Progress", bg=PANEL, fg=TEXT, font=self.font_heading).pack(anchor="w", padx=18, pady=(16, 8))
        self.task_progress_label = tk.Label(progress_card, text="", bg=PANEL, fg=MUTED, font=self.font_small)
        self.task_progress_label.pack(anchor="w", padx=18)
        self.task_progress_bar = ttk.Progressbar(
            progress_card,
            style="Dark.Horizontal.TProgressbar",
            maximum=100,
            value=0,
        )
        self.task_progress_bar.pack(fill="x", padx=18, pady=(12, 18))

        list_card = self._make_card(body)
        list_card.pack(fill="both", expand=True)
        tk.Label(list_card, text="Task Queue", bg=PANEL, fg=TEXT, font=self.font_heading).pack(anchor="w", padx=18, pady=(16, 8))
        self.tasks_list = ScrollableFrame(list_card, PANEL)
        self.tasks_list.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _build_exams_view(self):
        page, body = self._create_page(
            "Exam Schedule",
            "Track every exam by subject, location, and live countdown.",
        )
        self.views["Exam Schedule"] = page

        form_card = self._make_card(body)
        form_card.pack(fill="x", pady=(0, 16))
        form_inner = tk.Frame(form_card, bg=PANEL)
        form_inner.pack(fill="x", padx=18, pady=18)
        for column in range(4):
            form_inner.columnconfigure(column, weight=1)

        self.exam_subject_var = tk.StringVar()
        self.exam_date_var = tk.StringVar(value=(date.today() + timedelta(days=7)).isoformat())
        self.exam_time_var = tk.StringVar(value="09:00")
        self.exam_hall_var = tk.StringVar()

        labels = ["Subject", "Date (YYYY-MM-DD)", "Time (HH:MM)", "Hall"]
        vars_list = [self.exam_subject_var, self.exam_date_var, self.exam_time_var, self.exam_hall_var]
        for index, (label, variable) in enumerate(zip(labels, vars_list)):
            tk.Label(form_inner, text=label, bg=PANEL, fg=MUTED, font=self.font_small).grid(row=0, column=index, sticky="w", padx=(0 if index == 0 else 8, 0))
            entry = tk.Entry(
                form_inner,
                textvariable=variable,
                bg=PANEL_ALT,
                fg=TEXT,
                insertbackground=TEXT,
                relief="flat",
                font=self.font_body,
            )
            entry.grid(row=1, column=index, sticky="ew", padx=(0 if index == 0 else 8, 0), pady=(6, 0), ipady=8)

        self._make_action_button(form_inner, "Add Exam", self.add_exam).grid(row=1, column=4, padx=(12, 0), pady=(6, 0))

        list_card = self._make_card(body)
        list_card.pack(fill="both", expand=True)
        tk.Label(list_card, text="Upcoming & Past Exams", bg=PANEL, fg=TEXT, font=self.font_heading).pack(anchor="w", padx=18, pady=(16, 8))
        self.exams_list = ScrollableFrame(list_card, PANEL)
        self.exams_list.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _build_timetable_view(self):
        page, body = self._create_page(
            "Timetable",
            "Build a color-coded weekly plan so every class has a clear place.",
        )
        self.views["Timetable"] = page

        form_card = self._make_card(body)
        form_card.pack(fill="x", pady=(0, 16))
        form_inner = tk.Frame(form_card, bg=PANEL)
        form_inner.pack(fill="x", padx=18, pady=18)
        for column in range(4):
            form_inner.columnconfigure(column, weight=1)

        self.slot_day_var = tk.StringVar(value=DAYS[0])
        self.slot_time_var = tk.StringVar(value="09:00 - 10:30")
        self.slot_subject_var = tk.StringVar()
        self.slot_room_var = tk.StringVar()

        field_labels = ["Day", "Time Range", "Subject", "Room"]
        widgets = []

        day_box = ttk.Combobox(
            form_inner,
            values=DAYS,
            textvariable=self.slot_day_var,
            state="readonly",
            style="DarkAcademic.TCombobox",
            font=self.font_body,
        )
        widgets.append(day_box)

        for variable in [self.slot_time_var, self.slot_subject_var, self.slot_room_var]:
            widgets.append(
                tk.Entry(
                    form_inner,
                    textvariable=variable,
                    bg=PANEL_ALT,
                    fg=TEXT,
                    insertbackground=TEXT,
                    relief="flat",
                    font=self.font_body,
                )
            )

        for index, (label, widget) in enumerate(zip(field_labels, widgets)):
            tk.Label(form_inner, text=label, bg=PANEL, fg=MUTED, font=self.font_small).grid(row=0, column=index, sticky="w", padx=(0 if index == 0 else 8, 0))
            widget.grid(row=1, column=index, sticky="ew", padx=(0 if index == 0 else 8, 0), pady=(6, 0), ipady=8)

        self._make_action_button(form_inner, "Add Slot", self.add_timetable_slot).grid(row=1, column=4, padx=(12, 0), pady=(6, 0))

        board_frame = tk.Frame(body, bg=BG)
        board_frame.pack(fill="both", expand=True)
        for column in range(7):
            board_frame.columnconfigure(column, weight=1)

        self.timetable_columns = {}
        for index, day in enumerate(DAYS):
            column_card = self._make_card(board_frame)
            column_card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 4, 4 if index < 6 else 0))
            tk.Label(column_card, text=day, bg=PANEL, fg=TEXT, font=self.font_metric_small).pack(anchor="center", padx=10, pady=(14, 10))
            content = tk.Frame(column_card, bg=PANEL)
            content.pack(fill="both", expand=True, padx=10, pady=(0, 12))
            self.timetable_columns[day] = content

    def _build_grades_view(self):
        page, body = self._create_page(
            "Grade Tracker",
            "Adjust marks with sliders and watch your performance update visually.",
        )
        self.views["Grade Tracker"] = page

        top_card = self._make_card(body)
        top_card.pack(fill="x", pady=(0, 16))
        top_inner = tk.Frame(top_card, bg=PANEL)
        top_inner.pack(fill="x", padx=18, pady=18)
        top_inner.columnconfigure(0, weight=1)

        self.grade_subject_var = tk.StringVar()
        tk.Label(top_inner, text="New Subject", bg=PANEL, fg=MUTED, font=self.font_small).grid(row=0, column=0, sticky="w")
        tk.Entry(
            top_inner,
            textvariable=self.grade_subject_var,
            bg=PANEL_ALT,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=self.font_body,
        ).grid(row=1, column=0, sticky="ew", pady=(6, 0), ipady=8)
        self._make_action_button(top_inner, "Add Subject", self.add_grade_subject).grid(row=1, column=1, padx=(12, 0), pady=(6, 0))

        self.grade_average_label = tk.Label(top_inner, text="", bg=PANEL, fg=GOLD_SOFT, font=self.font_heading)
        self.grade_average_label.grid(row=0, column=2, rowspan=2, padx=(18, 0), sticky="e")

        split_frame = tk.Frame(body, bg=BG)
        split_frame.pack(fill="both", expand=True)
        split_frame.columnconfigure(0, weight=2)
        split_frame.columnconfigure(1, weight=3)

        controls_card = self._make_card(split_frame)
        controls_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        controls_header = tk.Frame(controls_card, bg=PANEL)
        controls_header.pack(fill="x", padx=18, pady=(16, 8))
        tk.Label(controls_header, text="Subject Sliders", bg=PANEL, fg=TEXT, font=self.font_heading).pack(anchor="w")
        self.grade_controls = ScrollableFrame(controls_card, PANEL)
        self.grade_controls.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        charts_column = tk.Frame(split_frame, bg=BG)
        charts_column.grid(row=0, column=1, sticky="nsew")
        charts_column.rowconfigure(0, weight=1)
        charts_column.rowconfigure(1, weight=1)

        bar_card = self._make_card(charts_column)
        bar_card.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        tk.Label(bar_card, text="Bar Chart", bg=PANEL, fg=TEXT, font=self.font_heading).pack(anchor="w", padx=18, pady=(16, 8))
        self.bar_chart_canvas = tk.Canvas(bar_card, bg=PANEL, highlightthickness=0, height=260)
        self.bar_chart_canvas.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.bar_chart_canvas.bind("<Configure>", lambda _event: self.draw_grade_charts())

        pie_card = self._make_card(charts_column)
        pie_card.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        tk.Label(pie_card, text="Pie Chart", bg=PANEL, fg=TEXT, font=self.font_heading).pack(anchor="w", padx=18, pady=(16, 8))
        self.pie_chart_canvas = tk.Canvas(pie_card, bg=PANEL, highlightthickness=0, height=260)
        self.pie_chart_canvas.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.pie_chart_canvas.bind("<Configure>", lambda _event: self.draw_grade_charts())

    def _build_timer_view(self):
        page, body = self._create_page(
            "Study Timer",
            "A Pomodoro space for focused work with a circular progress animation.",
        )
        self.views["Study Timer"] = page

        timer_scroll = ScrollableFrame(body, BG)
        timer_scroll.pack(fill="both", expand=True)

        timer_card = self._make_card(timer_scroll.content)
        timer_card.pack(fill="both", expand=True)

        center_frame = tk.Frame(timer_card, bg=PANEL)
        center_frame.pack(fill="both", expand=True, padx=20, pady=20)
        center_frame.columnconfigure(0, weight=3)
        center_frame.columnconfigure(1, weight=2)
        center_frame.rowconfigure(0, weight=1)

        left = tk.Frame(center_frame, bg=PANEL)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        self.timer_canvas = tk.Canvas(left, bg=PANEL, highlightthickness=0, height=360)
        self.timer_canvas.grid(row=0, column=0, sticky="nsew", pady=(10, 6))
        self.timer_canvas.bind("<Configure>", lambda _event: self.update_timer_display())
        self.timer_status_label = tk.Label(left, text=self.timer_status_text, bg=PANEL, fg=MUTED, font=self.font_body)
        self.timer_status_label.grid(row=1, column=0, pady=(0, 4))

        controls = tk.Frame(left, bg=PANEL)
        controls.grid(row=2, column=0, pady=(18, 0))
        self._make_action_button(controls, "Start", self.start_timer).grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self._make_action_button(controls, "Pause", self.pause_timer).grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        self._make_action_button(controls, "Reset", self.reset_timer).grid(row=1, column=0, padx=6, pady=6, sticky="ew")
        self._make_action_button(controls, "Switch Mode", self.switch_timer_mode).grid(row=1, column=1, padx=6, pady=6, sticky="ew")

        right = tk.Frame(center_frame, bg=PANEL)
        right.grid(row=0, column=1, sticky="nsew")

        settings_card = tk.Frame(right, bg=PANEL_ALT)
        settings_card.pack(fill="x", pady=(0, 14))
        tk.Label(settings_card, text="Pomodoro Settings", bg=PANEL_ALT, fg=TEXT, font=self.font_heading).pack(anchor="w", padx=18, pady=(16, 8))

        settings_form = tk.Frame(settings_card, bg=PANEL_ALT)
        settings_form.pack(fill="x", padx=18, pady=(0, 18))
        settings_form.columnconfigure(0, weight=1)
        settings_form.columnconfigure(1, weight=1)

        tk.Label(settings_form, text="Work (minutes)", bg=PANEL_ALT, fg=MUTED, font=self.font_small).grid(row=0, column=0, sticky="w")
        tk.Label(settings_form, text="Break (minutes)", bg=PANEL_ALT, fg=MUTED, font=self.font_small).grid(row=0, column=1, sticky="w", padx=(12, 0))

        tk.Entry(
            settings_form,
            textvariable=self.work_minutes_var,
            bg=BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=self.font_body,
        ).grid(row=1, column=0, sticky="ew", pady=(6, 0), ipady=8)

        tk.Entry(
            settings_form,
            textvariable=self.break_minutes_var,
            bg=BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=self.font_body,
        ).grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(6, 0), ipady=8)

        self._make_action_button(settings_form, "Apply", self.apply_timer_settings).grid(row=2, column=0, columnspan=2, pady=(12, 0), sticky="ew")

        tips_card = tk.Frame(right, bg=PANEL_ALT)
        tips_card.pack(fill="both", expand=True)
        tk.Label(tips_card, text="Focus Notes", bg=PANEL_ALT, fg=TEXT, font=self.font_heading).pack(anchor="w", padx=18, pady=(16, 8))
        for tip in [
            "Work sessions keep the golden ring in motion.",
            "When the countdown reaches zero, the mode switches automatically.",
            "Update settings any time and reset to start a fresh cycle.",
        ]:
            tk.Label(
                tips_card,
                text=f"- {tip}",
                bg=PANEL_ALT,
                fg=MUTED,
                font=self.font_body,
                wraplength=320,
                justify="left",
            ).pack(anchor="w", padx=18, pady=6)

    def _build_habits_view(self):
        page, body = self._create_page(
            "Habit Tracker",
            "Mark daily habits across the week and keep routine visible.",
        )
        self.views["Habit Tracker"] = page

        top_card = self._make_card(body)
        top_card.pack(fill="x", pady=(0, 16))
        top_inner = tk.Frame(top_card, bg=PANEL)
        top_inner.pack(fill="x", padx=18, pady=18)
        top_inner.columnconfigure(0, weight=1)

        self.habit_name_var = tk.StringVar()
        tk.Label(top_inner, text="Habit Name", bg=PANEL, fg=MUTED, font=self.font_small).grid(row=0, column=0, sticky="w")
        tk.Entry(
            top_inner,
            textvariable=self.habit_name_var,
            bg=PANEL_ALT,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=self.font_body,
        ).grid(row=1, column=0, sticky="ew", pady=(6, 0), ipady=8)
        self._make_action_button(top_inner, "Add Habit", self.add_habit).grid(row=1, column=1, padx=(12, 0), pady=(6, 0))
        self._make_action_button(top_inner, "Reset Week", self.reset_habit_week).grid(row=1, column=2, padx=(12, 0), pady=(6, 0))

        self.habit_summary_label = tk.Label(top_inner, text="", bg=PANEL, fg=GOLD_SOFT, font=self.font_body)
        self.habit_summary_label.grid(row=0, column=1, columnspan=2, sticky="e", padx=(14, 0))

        list_card = self._make_card(body)
        list_card.pack(fill="both", expand=True)
        tk.Label(list_card, text="Weekly Habit Board", bg=PANEL, fg=TEXT, font=self.font_heading).pack(anchor="w", padx=18, pady=(16, 8))
        self.habits_list = ScrollableFrame(list_card, PANEL)
        self.habits_list.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _build_notes_view(self):
        page, body = self._create_page(
            "Notes",
            "A free writing area for lecture summaries, reminders, and quick ideas.",
        )
        self.views["Notes"] = page

        notes_card = self._make_card(body)
        notes_card.pack(fill="both", expand=True)

        toolbar = tk.Frame(notes_card, bg=PANEL)
        toolbar.pack(fill="x", padx=18, pady=(16, 8))
        self.notes_status_label = tk.Label(toolbar, text="Autosave ready", bg=PANEL, fg=MUTED, font=self.font_small)
        self.notes_status_label.pack(side="left")
        self._make_action_button(toolbar, "Save Now", self.save_notes).pack(side="right")
        self._make_action_button(toolbar, "Clear Notes", self.clear_notes).pack(side="right", padx=(0, 8))

        editor_wrapper = tk.Frame(notes_card, bg=PANEL)
        editor_wrapper.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.notes_text = tk.Text(
            editor_wrapper,
            bg=PANEL_ALT,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=(self.sans_font, 12),
            wrap="word",
            padx=16,
            pady=16,
        )
        notes_scroll = tk.Scrollbar(editor_wrapper, orient="vertical", command=self.notes_text.yview)
        self.notes_text.configure(yscrollcommand=notes_scroll.set)
        self.notes_text.pack(side="left", fill="both", expand=True)
        notes_scroll.pack(side="right", fill="y")
        self.notes_text.insert("1.0", self.data.get("notes", ""))
        self.notes_text.bind("<KeyRelease>", self.schedule_notes_save)

    def _make_action_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=GOLD,
            fg=BG,
            activebackground=GOLD_SOFT,
            activeforeground=BG,
            relief="flat",
            bd=0,
            padx=14,
            pady=10,
            font=self.font_button,
            cursor="hand2",
        )

    def _refresh_all(self):
        self.render_tasks()
        self.render_exams()
        self.render_timetable()
        self.render_habits()
        self.update_timer_display()
        self.refresh_dashboard()

    def _refresh_time_sensitive_sections(self):
        self._update_today_label()
        self.render_exams()
        self.refresh_dashboard()
        self.after(60000, self._refresh_time_sensitive_sections)

    def _update_today_label(self):
        self.today_label.config(text=datetime.now().strftime("%A, %d %B %Y"))

    def show_view(self, name):
        if self.current_view == name:
            return

        if self.current_view:
            self.views[self.current_view].pack_forget()

        self.views[name].pack(fill="both", expand=True)
        self.current_view = name

        for section, button in self.nav_buttons.items():
            if section == name:
                button.configure(bg=PANEL_ALT, fg=GOLD_SOFT)
            else:
                button.configure(bg=SIDEBAR, fg=TEXT)

        if name == "Dashboard":
            self.refresh_dashboard()
        elif name == "To-Do List":
            self.render_tasks()
        elif name == "Exam Schedule":
            self.render_exams()
        elif name == "Timetable":
            self.render_timetable()
        elif name == "Study Timer":
            self.update_timer_display()
        elif name == "Habit Tracker":
            self.render_habits()

    def save_data(self):
        self.store.save(self.data)

    def clear_children(self, frame):
        for child in frame.winfo_children():
            child.destroy()

    def _priority_color(self, priority):
        colors = {
            "Urgent": RED,
            "High": GOLD,
            "Medium": BLUE,
            "Low": GREEN,
        }
        return colors.get(priority, MUTED)

    def _sorted_tasks(self):
        return sorted(
            self.data.get("tasks", []),
            key=lambda task: (
                task.get("done", False),
                PRIORITY_ORDER.get(task.get("priority", "Low"), 99),
                task.get("title", "").lower(),
            ),
        )

    def add_task(self):
        title = self.task_title_var.get().strip()
        if not title:
            messagebox.showwarning("Missing Task", "Please write a task title first.")
            return

        self.data["tasks"].append(
            {
                "id": make_id("task"),
                "title": title,
                "priority": self.task_priority_var.get(),
                "done": False,
            }
        )
        self.task_title_var.set("")
        self.task_priority_var.set("High")
        self.save_data()
        self.render_tasks()
        self.refresh_dashboard()
        self.task_entry.focus_set()

    def toggle_task(self, task_id, done):
        for task in self.data.get("tasks", []):
            if task["id"] == task_id:
                task["done"] = bool(done)
                break
        self.save_data()
        self.render_tasks()
        self.refresh_dashboard()

    def delete_task(self, task_id):
        self.data["tasks"] = [task for task in self.data.get("tasks", []) if task["id"] != task_id]
        self.save_data()
        self.render_tasks()
        self.refresh_dashboard()

    def render_tasks(self):
        self.clear_children(self.tasks_list.content)
        tasks = self._sorted_tasks()
        total = len(tasks)
        completed = sum(1 for task in tasks if task.get("done"))
        progress = (completed / total * 100) if total else 0

        self.task_progress_label.config(
            text=f"{completed} of {total} tasks completed" if total else "No tasks yet. Add your first study task above."
        )
        self.task_progress_bar.configure(value=progress)

        if not tasks:
            tk.Label(
                self.tasks_list.content,
                text="No tasks added yet.",
                bg=PANEL,
                fg=MUTED,
                font=self.font_body,
            ).pack(anchor="w", padx=12, pady=12)
            return

        for task in tasks:
            card = tk.Frame(
                self.tasks_list.content,
                bg=PANEL_ALT if not task.get("done") else "#1e2620",
                highlightbackground=self._priority_color(task.get("priority", "Low")),
                highlightthickness=1,
            )
            card.pack(fill="x", pady=6, padx=4)

            top = tk.Frame(card, bg=card["bg"])
            top.pack(fill="x", padx=14, pady=12)

            done_var = tk.BooleanVar(value=task.get("done", False))
            tk.Checkbutton(
                top,
                variable=done_var,
                bg=card["bg"],
                activebackground=card["bg"],
                selectcolor=card["bg"],
                fg=TEXT,
                command=lambda task_id=task["id"], var=done_var: self.toggle_task(task_id, var.get()),
            ).pack(side="left")

            task_font = self.font_body_strike if task.get("done") else self.font_body
            title_color = MUTED if task.get("done") else TEXT
            tk.Label(
                top,
                text=task.get("title", ""),
                bg=card["bg"],
                fg=title_color,
                font=task_font,
            ).pack(side="left", padx=(6, 10))

            tk.Label(
                top,
                text=task.get("priority", "Low"),
                bg=self._priority_color(task.get("priority", "Low")),
                fg=TEXT,
                font=self.font_small,
                padx=10,
                pady=4,
            ).pack(side="right")

            tk.Button(
                top,
                text="Delete",
                command=lambda task_id=task["id"]: self.delete_task(task_id),
                bg=card["bg"],
                fg=RED,
                activebackground=card["bg"],
                activeforeground=RED,
                bd=0,
                relief="flat",
                font=self.font_small,
                cursor="hand2",
            ).pack(side="right", padx=(0, 10))

    def _exam_datetime(self, exam):
        try:
            return datetime.strptime(f"{exam['date']} {exam['time']}", "%Y-%m-%d %H:%M")
        except (KeyError, ValueError):
            return None

    def _sorted_exams(self):
        return sorted(
            self.data.get("exams", []),
            key=lambda exam: self._exam_datetime(exam) or datetime.max,
        )

    def add_exam(self):
        subject = self.exam_subject_var.get().strip()
        exam_date = self.exam_date_var.get().strip()
        exam_time = self.exam_time_var.get().strip()
        hall = self.exam_hall_var.get().strip()

        if not all([subject, exam_date, exam_time, hall]):
            messagebox.showwarning("Missing Details", "Please fill in subject, date, time, and hall.")
            return

        try:
            datetime.strptime(f"{exam_date} {exam_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Invalid Date", "Use date format YYYY-MM-DD and time format HH:MM.")
            return

        self.data["exams"].append(
            {
                "id": make_id("exam"),
                "subject": subject,
                "date": exam_date,
                "time": exam_time,
                "hall": hall,
            }
        )
        self.exam_subject_var.set("")
        self.exam_hall_var.set("")
        self.save_data()
        self.render_exams()
        self.refresh_dashboard()

    def delete_exam(self, exam_id):
        self.data["exams"] = [exam for exam in self.data.get("exams", []) if exam["id"] != exam_id]
        self.save_data()
        self.render_exams()
        self.refresh_dashboard()

    def _countdown_text(self, target_dt):
        if not target_dt:
            return "Invalid schedule"
        delta = target_dt - datetime.now()
        total_seconds = int(delta.total_seconds())
        if total_seconds < 0:
            overdue = abs(total_seconds)
            days = overdue // 86400
            hours = (overdue % 86400) // 3600
            minutes = (overdue % 3600) // 60
            if days:
                return f"Passed {days}d {hours}h ago"
            if hours:
                return f"Passed {hours}h {minutes}m ago"
            return f"Passed {max(minutes, 1)}m ago"

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        if days:
            return f"{days}d {hours}h remaining"
        if hours:
            return f"{hours}h {minutes}m remaining"
        return f"{max(minutes, 1)}m remaining"

    def _countdown_brief(self, target_dt):
        if not target_dt:
            return "N/A"
        delta = target_dt - datetime.now()
        total_seconds = int(delta.total_seconds())
        if total_seconds <= 0:
            return "Started"
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        if days:
            return f"{days}d {hours}h"
        if hours:
            return f"{hours}h {minutes}m"
        return f"{max(minutes, 1)}m"

    def render_exams(self):
        self.clear_children(self.exams_list.content)
        exams = self._sorted_exams()

        if not exams:
            tk.Label(
                self.exams_list.content,
                text="No exams scheduled yet.",
                bg=PANEL,
                fg=MUTED,
                font=self.font_body,
            ).pack(anchor="w", padx=12, pady=12)
            return

        for exam in exams:
            exam_dt = self._exam_datetime(exam)
            countdown = self._countdown_text(exam_dt)
            is_soon = exam_dt and 0 <= (exam_dt - datetime.now()).total_seconds() <= 72 * 3600
            is_past = exam_dt and (exam_dt - datetime.now()).total_seconds() < 0
            border = RED if is_soon else OUTLINE
            if is_past:
                border = PURPLE_GREY

            card = tk.Frame(
                self.exams_list.content,
                bg=PANEL_ALT,
                highlightbackground=border,
                highlightthickness=1,
            )
            card.pack(fill="x", padx=4, pady=6)

            top = tk.Frame(card, bg=PANEL_ALT)
            top.pack(fill="x", padx=14, pady=(14, 8))
            tk.Label(top, text=exam.get("subject", ""), bg=PANEL_ALT, fg=TEXT, font=self.font_heading).pack(side="left")
            tk.Button(
                top,
                text="Delete",
                command=lambda exam_id=exam["id"]: self.delete_exam(exam_id),
                bg=PANEL_ALT,
                fg=RED,
                activebackground=PANEL_ALT,
                activeforeground=RED,
                relief="flat",
                bd=0,
                font=self.font_small,
                cursor="hand2",
            ).pack(side="right")

            details = f"{exam.get('date', '')} at {exam.get('time', '')}  |  {exam.get('hall', '')}"
            tk.Label(card, text=details, bg=PANEL_ALT, fg=MUTED, font=self.font_body).pack(anchor="w", padx=14)
            tk.Label(
                card,
                text=countdown,
                bg=PANEL_ALT,
                fg=RED if is_soon else (MUTED if is_past else GOLD_SOFT),
                font=self.font_small,
            ).pack(anchor="w", padx=14, pady=(8, 14))

    def _subject_color(self, subject):
        if not subject:
            return GOLD
        index = sum(ord(letter) for letter in subject) % len(SUBJECT_COLORS)
        return SUBJECT_COLORS[index]

    def add_timetable_slot(self):
        day = self.slot_day_var.get().strip()
        time_range = self.slot_time_var.get().strip()
        subject = self.slot_subject_var.get().strip()
        room = self.slot_room_var.get().strip()

        if not all([day, time_range, subject, room]):
            messagebox.showwarning("Missing Details", "Please fill in day, time, subject, and room.")
            return

        self.data["timetable"].append(
            {
                "id": make_id("slot"),
                "day": day,
                "time": time_range,
                "subject": subject,
                "room": room,
            }
        )
        self.slot_time_var.set("09:00 - 10:30")
        self.slot_subject_var.set("")
        self.slot_room_var.set("")
        self.save_data()
        self.render_timetable()

    def delete_timetable_slot(self, slot_id):
        self.data["timetable"] = [slot for slot in self.data.get("timetable", []) if slot["id"] != slot_id]
        self.save_data()
        self.render_timetable()

    def render_timetable(self):
        for day, column in self.timetable_columns.items():
            self.clear_children(column)
            day_slots = [
                slot for slot in self.data.get("timetable", [])
                if slot.get("day") == day
            ]
            day_slots.sort(key=lambda slot: slot.get("time", ""))

            if not day_slots:
                tk.Label(
                    column,
                    text="No classes",
                    bg=PANEL,
                    fg=MUTED,
                    font=self.font_small,
                ).pack(anchor="center", pady=12)
                continue

            for slot in day_slots:
                slot_card = tk.Frame(
                    column,
                    bg=self._subject_color(slot.get("subject", "")),
                    highlightbackground=OUTLINE,
                    highlightthickness=1,
                )
                slot_card.pack(fill="x", pady=5)

                top = tk.Frame(slot_card, bg=slot_card["bg"])
                top.pack(fill="x", padx=10, pady=(10, 4))
                tk.Label(
                    top,
                    text=slot.get("subject", ""),
                    bg=slot_card["bg"],
                    fg=TEXT,
                    font=self.font_body,
                ).pack(side="left")
                tk.Button(
                    top,
                    text="x",
                    command=lambda slot_id=slot["id"]: self.delete_timetable_slot(slot_id),
                    bg=slot_card["bg"],
                    fg=TEXT,
                    activebackground=slot_card["bg"],
                    activeforeground=TEXT,
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                ).pack(side="right")

                tk.Label(
                    slot_card,
                    text=slot.get("time", ""),
                    bg=slot_card["bg"],
                    fg=TEXT,
                    font=self.font_small,
                ).pack(anchor="w", padx=10)
                tk.Label(
                    slot_card,
                    text=slot.get("room", ""),
                    bg=slot_card["bg"],
                    fg=TEXT,
                    font=self.font_small,
                ).pack(anchor="w", padx=10, pady=(2, 10))

    def add_grade_subject(self):
        subject = self.grade_subject_var.get().strip()
        if not subject:
            messagebox.showwarning("Missing Subject", "Please write a subject name first.")
            return

        existing = {item["subject"].lower() for item in self.data.get("grades", [])}
        if subject.lower() in existing:
            messagebox.showinfo("Already Exists", "This subject is already in the grade tracker.")
            return

        self.data["grades"].append({"id": make_id("grade"), "subject": subject, "score": 50})
        self.grade_subject_var.set("")
        self.save_data()
        self.render_grade_controls()
        self.draw_grade_charts()
        self.refresh_dashboard()

    def delete_grade_subject(self, subject_name):
        self.data["grades"] = [item for item in self.data.get("grades", []) if item["subject"] != subject_name]
        self.save_data()
        self.render_grade_controls()
        self.draw_grade_charts()
        self.refresh_dashboard()

    def update_grade_score(self, subject_name, raw_value, value_label):
        score = int(float(raw_value))
        for item in self.data.get("grades", []):
            if item["subject"] == subject_name:
                item["score"] = score
                break
        value_label.config(text=f"{score}%")
        self.save_data()
        self.grade_average_label.config(text=f"Average: {self._average_grade():.1f}%")
        self.draw_grade_charts()
        self.refresh_dashboard()

    def render_grade_controls(self):
        self.clear_children(self.grade_controls.content)
        grades = sorted(self.data.get("grades", []), key=lambda item: item.get("subject", "").lower())
        self.grade_average_label.config(text=f"Average: {self._average_grade():.1f}%")

        if not grades:
            tk.Label(
                self.grade_controls.content,
                text="No subjects yet. Add one above.",
                bg=PANEL,
                fg=MUTED,
                font=self.font_body,
            ).pack(anchor="w", padx=12, pady=12)
            return

        for item in grades:
            row = tk.Frame(self.grade_controls.content, bg=PANEL_ALT, highlightbackground=OUTLINE, highlightthickness=1)
            row.pack(fill="x", padx=4, pady=6)

            top = tk.Frame(row, bg=PANEL_ALT)
            top.pack(fill="x", padx=14, pady=(12, 6))
            tk.Label(top, text=item["subject"], bg=PANEL_ALT, fg=TEXT, font=self.font_body).pack(side="left")
            value_label = tk.Label(top, text=f"{item['score']}%", bg=PANEL_ALT, fg=GOLD_SOFT, font=self.font_small)
            value_label.pack(side="right")
            tk.Button(
                top,
                text="Delete",
                command=lambda subject=item["subject"]: self.delete_grade_subject(subject),
                bg=PANEL_ALT,
                fg=RED,
                activebackground=PANEL_ALT,
                activeforeground=RED,
                relief="flat",
                bd=0,
                font=self.font_small,
                cursor="hand2",
            ).pack(side="right", padx=(0, 12))

            scale = tk.Scale(
                row,
                from_=0,
                to=100,
                orient="horizontal",
                showvalue=False,
                resolution=1,
                bg=PANEL_ALT,
                fg=TEXT,
                troughcolor=BG,
                activebackground=GOLD,
                highlightthickness=0,
                length=340,
                command=lambda value, subject=item["subject"], label=value_label: self.update_grade_score(subject, value, label),
            )
            scale.set(item["score"])
            scale.pack(fill="x", padx=14, pady=(0, 12))

    def _average_grade(self):
        grades = self.data.get("grades", [])
        if not grades:
            return 0.0
        return sum(item.get("score", 0) for item in grades) / len(grades)

    def draw_grade_charts(self):
        self._draw_bar_chart()
        self._draw_pie_chart()

    def _draw_bar_chart(self):
        canvas = self.bar_chart_canvas
        canvas.delete("all")
        grades = self.data.get("grades", [])
        if not grades:
            canvas.create_text(240, 120, text="No grade data yet.", fill=MUTED, font=self.font_body)
            return

        width = max(canvas.winfo_width(), 520)
        height = max(canvas.winfo_height(), 250)
        left_margin = 44
        bottom_margin = 36
        top_margin = 18
        right_margin = 18
        plot_width = width - left_margin - right_margin
        plot_height = height - top_margin - bottom_margin

        canvas.create_line(left_margin, top_margin, left_margin, height - bottom_margin, fill=OUTLINE, width=2)
        canvas.create_line(left_margin, height - bottom_margin, width - right_margin, height - bottom_margin, fill=OUTLINE, width=2)

        step = plot_width / max(len(grades), 1)
        bar_width = min(46, step * 0.55)

        for index, item in enumerate(grades):
            x_center = left_margin + (index + 0.5) * step
            bar_height = plot_height * (item.get("score", 0) / 100)
            x0 = x_center - bar_width / 2
            y0 = height - bottom_margin - bar_height
            x1 = x_center + bar_width / 2
            y1 = height - bottom_margin
            color = self._subject_color(item.get("subject", ""))
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline=color)
            canvas.create_text(x_center, y0 - 10, text=f"{item.get('score', 0)}%", fill=GOLD_SOFT, font=self.font_small)
            label = item.get("subject", "")[:12]
            canvas.create_text(x_center, height - 14, text=label, fill=MUTED, font=self.font_small)

        for percentage in [25, 50, 75, 100]:
            y = height - bottom_margin - (plot_height * percentage / 100)
            canvas.create_line(left_margin, y, width - right_margin, y, fill="#2a2431")
            canvas.create_text(20, y, text=str(percentage), fill=MUTED, font=self.font_small)

    def _draw_pie_chart(self):
        canvas = self.pie_chart_canvas
        canvas.delete("all")
        grades = self.data.get("grades", [])
        if not grades:
            canvas.create_text(240, 120, text="No grade data yet.", fill=MUTED, font=self.font_body)
            return

        width = max(canvas.winfo_width(), 520)
        height = max(canvas.winfo_height(), 250)
        diameter = min(height - 40, 180)
        x0 = 26
        y0 = 24
        x1 = x0 + diameter
        y1 = y0 + diameter

        total = sum(max(item.get("score", 0), 1) for item in grades)
        start = 90
        for item in grades:
            value = max(item.get("score", 0), 1)
            extent = -(value / total) * 360
            color = self._subject_color(item.get("subject", ""))
            canvas.create_arc(x0, y0, x1, y1, start=start, extent=extent, fill=color, outline=PANEL, width=2)
            start += extent

        canvas.create_oval(
            x0 + diameter * 0.28,
            y0 + diameter * 0.28,
            x1 - diameter * 0.28,
            y1 - diameter * 0.28,
            fill=PANEL,
            outline=PANEL,
        )
        canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2 - 8, text="Average", fill=MUTED, font=self.font_small)
        canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2 + 16, text=f"{self._average_grade():.1f}%", fill=GOLD_SOFT, font=self.font_heading)

        legend_x = x1 + 24
        legend_y = 34
        for item in grades:
            color = self._subject_color(item.get("subject", ""))
            canvas.create_rectangle(legend_x, legend_y, legend_x + 14, legend_y + 14, fill=color, outline=color)
            canvas.create_text(
                legend_x + 22,
                legend_y + 7,
                text=f"{item.get('subject', '')} ({item.get('score', 0)}%)",
                anchor="w",
                fill=TEXT,
                font=self.font_small,
            )
            legend_y += 24

    def _timer_minutes_from_var(self, variable, label):
        value = variable.get().strip()
        try:
            minutes = int(value)
        except ValueError as error:
            raise ValueError(f"{label} minutes must be a whole number.") from error
        if minutes <= 0:
            raise ValueError(f"{label} minutes must be greater than zero.")
        return minutes

    def _current_mode_minutes(self):
        if self.timer_mode == "work":
            return int(self.data.get("timer_settings", {}).get("work_minutes", 25))
        return int(self.data.get("timer_settings", {}).get("break_minutes", 5))

    def apply_timer_settings(self):
        try:
            work_minutes = self._timer_minutes_from_var(self.work_minutes_var, "Work")
            break_minutes = self._timer_minutes_from_var(self.break_minutes_var, "Break")
        except ValueError as error:
            messagebox.showerror("Invalid Timer Value", str(error))
            return False

        self.data["timer_settings"] = {
            "work_minutes": work_minutes,
            "break_minutes": break_minutes,
        }
        self.save_data()

        if not self.timer_running:
            self.timer_total_seconds = self._current_mode_minutes() * 60
            self.timer_remaining_seconds = self.timer_total_seconds

        self.timer_status_label.config(text="Timer settings saved.")
        self.update_timer_display()
        return True

    def start_timer(self):
        if self.timer_running:
            return

        session_in_progress = 0 < self.timer_remaining_seconds < self.timer_total_seconds

        if session_in_progress:
            self.timer_status_label.config(
                text="Focus session resumed." if self.timer_mode == "work" else "Break session resumed."
            )
        else:
            if not self.apply_timer_settings():
                return
            self.timer_status_label.config(
                text="Focus session running." if self.timer_mode == "work" else "Break session running."
            )

        self.timer_running = True
        self._schedule_timer_tick()

    def _schedule_timer_tick(self):
        self.update_timer_display()
        if self.timer_running:
            self.timer_job = self.after(1000, self._tick_timer)

    def _tick_timer(self):
        if not self.timer_running:
            return

        if self.timer_remaining_seconds > 0:
            self.timer_remaining_seconds -= 1
            self.update_timer_display()

        if self.timer_remaining_seconds <= 0:
            self.bell()
            next_mode = "break" if self.timer_mode == "work" else "work"
            self.timer_mode = next_mode
            self.timer_total_seconds = self._current_mode_minutes() * 60
            self.timer_remaining_seconds = self.timer_total_seconds
            self.timer_status_label.config(
                text="Break started automatically." if next_mode == "break" else "Work session started automatically."
            )

        if self.timer_running:
            self.timer_job = self.after(1000, self._tick_timer)

    def pause_timer(self):
        self.timer_running = False
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None
        self.timer_status_label.config(text="Timer paused.")
        self.update_timer_display()

    def reset_timer(self):
        self.pause_timer()
        self.timer_total_seconds = self._current_mode_minutes() * 60
        self.timer_remaining_seconds = self.timer_total_seconds
        self.timer_status_label.config(text="Timer reset for the current mode.")
        self.update_timer_display()

    def switch_timer_mode(self):
        self.pause_timer()
        self.timer_mode = "break" if self.timer_mode == "work" else "work"
        self.timer_total_seconds = self._current_mode_minutes() * 60
        self.timer_remaining_seconds = self.timer_total_seconds
        self.timer_status_label.config(text="Break mode ready." if self.timer_mode == "break" else "Work mode ready.")
        self.update_timer_display()

    def update_timer_display(self):
        canvas = self.timer_canvas
        canvas.delete("all")

        width = max(canvas.winfo_width(), 260)
        height = max(canvas.winfo_height(), 260)
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) * 0.28
        time_font_size = max(24, int(min(width, height) * 0.08))

        color = GOLD if self.timer_mode == "work" else BLUE
        progress = 0
        if self.timer_total_seconds > 0:
            progress = 1 - (self.timer_remaining_seconds / self.timer_total_seconds)

        canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            outline=OUTLINE,
            width=18,
        )
        canvas.create_arc(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            start=90,
            extent=-(progress * 360),
            style="arc",
            outline=color,
            width=18,
        )

        remaining = max(self.timer_remaining_seconds, 0)
        minutes = remaining // 60
        seconds = remaining % 60
        canvas.create_text(center_x, center_y - 26, text=self.timer_mode.upper(), fill=MUTED, font=self.font_small)
        canvas.create_text(center_x, center_y + 8, text=f"{minutes:02d}:{seconds:02d}", fill=TEXT, font=(self.serif_font, time_font_size, "bold"))
        canvas.create_text(center_x, center_y + 46, text="Pomodoro cycle", fill=GOLD_SOFT, font=self.font_small)

    def add_habit(self):
        name = self.habit_name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Habit", "Please write a habit name first.")
            return

        self.data["habits"].append({"id": make_id("habit"), "name": name, "week": [0, 0, 0, 0, 0, 0, 0]})
        self.habit_name_var.set("")
        self.save_data()
        self.render_habits()
        self.refresh_dashboard()

    def delete_habit(self, habit_id):
        self.data["habits"] = [habit for habit in self.data.get("habits", []) if habit["id"] != habit_id]
        self.save_data()
        self.render_habits()
        self.refresh_dashboard()

    def toggle_habit_day(self, habit_id, day_index):
        for habit in self.data.get("habits", []):
            if habit["id"] == habit_id:
                current = bool(habit["week"][day_index])
                habit["week"][day_index] = 0 if current else 1
                break
        self.save_data()
        self.render_habits()
        self.refresh_dashboard()

    def reset_habit_week(self):
        if not self.data.get("habits"):
            return
        for habit in self.data["habits"]:
            habit["week"] = [0, 0, 0, 0, 0, 0, 0]
        self.save_data()
        self.render_habits()
        self.refresh_dashboard()

    def render_habits(self):
        self.clear_children(self.habits_list.content)
        habits = self.data.get("habits", [])
        total_cells = max(len(habits) * 7, 1)
        completed_cells = sum(sum(int(value) for value in habit.get("week", [])) for habit in habits)
        percentage = (completed_cells / total_cells * 100) if habits else 0
        self.habit_summary_label.config(text=f"Weekly consistency: {percentage:.0f}%")

        if not habits:
            tk.Label(
                self.habits_list.content,
                text="No habits added yet.",
                bg=PANEL,
                fg=MUTED,
                font=self.font_body,
            ).pack(anchor="w", padx=12, pady=12)
            return

        header = tk.Frame(self.habits_list.content, bg=PANEL)
        header.pack(fill="x", padx=4, pady=(0, 8))
        tk.Label(header, text="Habit", bg=PANEL, fg=MUTED, font=self.font_small, width=20, anchor="w").pack(side="left")
        for short in DAY_SHORT:
            tk.Label(header, text=short, bg=PANEL, fg=MUTED, font=self.font_small, width=5).pack(side="left", padx=2)

        for habit in habits:
            row = tk.Frame(self.habits_list.content, bg=PANEL_ALT, highlightbackground=OUTLINE, highlightthickness=1)
            row.pack(fill="x", padx=4, pady=5)

            name_frame = tk.Frame(row, bg=PANEL_ALT)
            name_frame.pack(side="left", fill="y", padx=(14, 10), pady=12)
            tk.Label(name_frame, text=habit.get("name", ""), bg=PANEL_ALT, fg=TEXT, font=self.font_body, width=20, anchor="w").pack(side="left")
            tk.Button(
                name_frame,
                text="Delete",
                command=lambda habit_id=habit["id"]: self.delete_habit(habit_id),
                bg=PANEL_ALT,
                fg=RED,
                activebackground=PANEL_ALT,
                activeforeground=RED,
                relief="flat",
                bd=0,
                font=self.font_small,
                cursor="hand2",
            ).pack(side="left", padx=(8, 0))

            week_frame = tk.Frame(row, bg=PANEL_ALT)
            week_frame.pack(side="left", padx=(0, 10), pady=10)
            week = habit.get("week", [0, 0, 0, 0, 0, 0, 0])
            for index, value in enumerate(week[:7]):
                active = bool(value)
                tk.Button(
                    week_frame,
                    text=DAY_SHORT[index],
                    width=5,
                    command=lambda habit_id=habit["id"], idx=index: self.toggle_habit_day(habit_id, idx),
                    bg=GOLD if active else BG,
                    fg=BG if active else TEXT,
                    activebackground=GOLD_SOFT if active else PANEL,
                    activeforeground=BG if active else TEXT,
                    relief="flat",
                    bd=0,
                    font=self.font_small,
                    padx=4,
                    pady=6,
                    cursor="hand2",
                ).pack(side="left", padx=2)

    def schedule_notes_save(self, _event=None):
        self.notes_status_label.config(text="Typing... autosave pending")
        if self.note_save_job:
            self.after_cancel(self.note_save_job)
        self.note_save_job = self.after(700, self.save_notes)

    def save_notes(self):
        if self.note_save_job:
            self.after_cancel(self.note_save_job)
            self.note_save_job = None

        self.data["notes"] = self.notes_text.get("1.0", "end-1c")
        self.save_data()
        self.notes_status_label.config(text=f"Saved at {datetime.now().strftime('%H:%M:%S')}")

    def clear_notes(self):
        if not messagebox.askyesno("Clear Notes", "Do you want to erase all notes?"):
            return
        self.notes_text.delete("1.0", "end")
        self.save_notes()

    def refresh_dashboard(self):
        tasks = self.data.get("tasks", [])
        pending_tasks = sum(1 for task in tasks if not task.get("done"))
        completed_tasks = sum(1 for task in tasks if task.get("done"))
        total_tasks = len(tasks)
        progress = (completed_tasks / total_tasks * 100) if total_tasks else 0

        future_exams = [exam for exam in self._sorted_exams() if self._exam_datetime(exam) and self._exam_datetime(exam) >= datetime.now()]
        next_exam = future_exams[0] if future_exams else None
        next_exam_dt = self._exam_datetime(next_exam) if next_exam else None

        habits = self.data.get("habits", [])
        habit_cells = len(habits) * 7
        habit_done = sum(sum(int(value) for value in habit.get("week", [])) for habit in habits)
        habit_rate = (habit_done / habit_cells * 100) if habit_cells else 0

        self.dashboard_stats["tasks"][0].config(text=str(pending_tasks))
        self.dashboard_stats["tasks"][1].config(text=f"{completed_tasks} completed of {total_tasks}" if total_tasks else "No tasks added yet")

        self.dashboard_stats["progress"][0].config(text=f"{progress:.0f}%")
        self.dashboard_stats["progress"][1].config(text="Overall task completion")

        self.dashboard_stats["habits"][0].config(text=f"{habit_rate:.0f}%")
        if habits:
            self.dashboard_stats["habits"][1].config(text=f"{habit_done} checks completed across {len(habits)} habits")
        else:
            self.dashboard_stats["habits"][1].config(text="No habits tracked yet")

        exam_value = self._countdown_brief(next_exam_dt) if next_exam else "None"
        exam_caption = f"{next_exam['subject']} | {next_exam['hall']}" if next_exam else "No upcoming exams scheduled"
        self.dashboard_stats["exam"][0].config(text=exam_value)
        self.dashboard_stats["exam"][1].config(text=exam_caption)

        self.clear_children(self.dashboard_task_preview)
        priority_tasks = [task for task in self._sorted_tasks() if not task.get("done")][:5]
        if not priority_tasks:
            tk.Label(self.dashboard_task_preview, text="Your queue is clear for now.", bg=PANEL, fg=MUTED, font=self.font_body).pack(anchor="w")
        for task in priority_tasks:
            row = tk.Frame(self.dashboard_task_preview, bg=PANEL)
            row.pack(fill="x", pady=6)
            tk.Label(row, text="-", bg=PANEL, fg=self._priority_color(task.get("priority", "Low")), font=self.font_body).pack(side="left")
            tk.Label(row, text=task.get("title", ""), bg=PANEL, fg=TEXT, font=self.font_body, wraplength=260, justify="left").pack(side="left", padx=(6, 8))
            tk.Label(row, text=task.get("priority", "Low"), bg=PANEL, fg=MUTED, font=self.font_small).pack(side="right")

        self.clear_children(self.dashboard_exam_preview)
        if not future_exams:
            tk.Label(self.dashboard_exam_preview, text="Nothing upcoming. Add an exam to activate the countdown.", bg=PANEL, fg=MUTED, font=self.font_body, wraplength=280, justify="left").pack(anchor="w")
        else:
            for exam in future_exams[:3]:
                exam_dt = self._exam_datetime(exam)
                row = tk.Frame(self.dashboard_exam_preview, bg=PANEL)
                row.pack(fill="x", pady=8)
                tk.Label(row, text=exam.get("subject", ""), bg=PANEL, fg=TEXT, font=self.font_body).pack(anchor="w")
                tk.Label(
                    row,
                    text=f"{exam.get('date', '')} | {exam.get('time', '')} | {self._countdown_text(exam_dt)}",
                    bg=PANEL,
                    fg=GOLD_SOFT,
                    font=self.font_small,
                    wraplength=290,
                    justify="left",
                ).pack(anchor="w", pady=(2, 0))

        quote_index = date.today().timetuple().tm_yday % len(QUOTES)
        self.dashboard_quote_label.config(text=f"\"{QUOTES[quote_index]}\"")
        self.dashboard_quote_hint.config(text=f"Weekly habit completion is currently {habit_rate:.0f}%.")

    def on_close(self):
        self.save_notes()
        self.pause_timer()
        self.destroy()


if __name__ == "__main__":
    app = StudentPlannerApp()
    app.mainloop()
