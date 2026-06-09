import subprocess
import sys


def install_dependencies():
    packages = {
        "pandas": "pandas",
        "PIL": "pillow",
        "matplotlib": "matplotlib",
        "kagglehub": "kagglehub",
    }
    for module, pip_package in packages.items():
        try:
            __import__(module)
        except ImportError:
            print(f"Installing '{pip_package}'...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pip_package]
                )
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {pip_package}: {e}")
                sys.exit(1)


install_dependencies()

import math
from pathlib import Path

import subprocess
import sys


def install_dependencies():
    packages = {
        "pandas": "pandas",
        "PIL": "pillow",
        "matplotlib": "matplotlib",
        "kagglehub": "kagglehub",
    }
    for module, pip_package in packages.items():
        try:
            __import__(module)
        except ImportError:
            print(f"Installing '{pip_package}'...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pip_package]
                )
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {pip_package}: {e}")
                sys.exit(1)


install_dependencies()

import math
from pathlib import Path

import tkinter as tk
from tkinter import ttk

from tkinter import ttk

import pandas as pd
from PIL import Image, ImageTk
from PIL import Image, ImageTk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

import combat_engine as ce

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
BG = "#12151c"
PANEL = "#1b1f2a"
PANEL_LIGHT = "#252a38"
ACCENT = "#4ea1ff"
ACCENT_DIM = "#2d6ab0"
TEXT = "#e6e9f0"
TEXT_DIM = "#8b93a7"
GOOD = "#46d369"
WARN = "#f5a623"
BAD = "#e0524f"
FONT = "Segoe UI" if sys.platform == "win32" else "DejaVu Sans"

BASE_DIR = Path(__file__).parent
LOCAL_CSV = BASE_DIR / "fighter_aircraft_dataset_v10.csv"
IMG_DIR = BASE_DIR / "img"
KAGGLE_SLUG = "oxcartcorporation/military-aircraft-dataset"


def resolve_csv_path():
    try:
        print("Attempting Kaggle download...")
        for dirname, _, filenames in os.walk('/kaggle/input'):
            for filename in filenames:
                print(os.path.join(dirname, filename))
                df = pd.read_csv('/kaggle/input/datasets/oxcartcorporation/military-aircraft-dataset/fighter_aircraft_dataset_v10.csv')
    except Exception as e:
        print(f"Kaggle unavailable ({e}); using local CSV.")
    if LOCAL_CSV.exists():
        return LOCAL_CSV
    print("ERROR: no data source available.")
    sys.exit(1)


def stealth_from_rcs(rcs):
    if rcs <= 0:
        return 1.0
    return max(0.0, min(1.0, 1 - (math.log10(max(rcs, 1e-6)) + 4) / 8.5))


def build_aircraft(row):
    return {
        "name": row["Aircraft"],
        "country": row["Country"],
        "generation": ce.parse_generation(row["Generation"]),
        "rcs": row["RCS_m2"],
        "radar": row["Radar_Score"] * 10,
        "missile": row["Missile_Score"],
        "ew": row["EW_Score"],
        "maneuver": min(1.0, row["Missile_Score"] + (0.1 if row["Thrust_Vectoring"] == "Yes" else 0)),
        "stealth": stealth_from_rcs(row["RCS_m2"]),
        "range": row["Combat_Radius_km"],
        "speed": row["Max_Speed_kmh"],
        "ceiling": row["Service_Ceiling_m"],
        "cost": row["Unit_Cost_M_USD"],
        "cost_hour": row["Cost_per_Flight_Hour_USD"],
        "role": row["Role"],
    }


CSV_PATH = resolve_csv_path()
DF = pd.read_csv(CSV_PATH)
AIRCRAFT = {row["Aircraft"]: build_aircraft(row) for _, row in DF.iterrows()}
COUNTRIES = {}
for ac in AIRCRAFT.values():
    COUNTRIES.setdefault(ac["country"], []).append(ac["name"])

ROLE_TO_MISSIONS = {
    "Air Superiority": ["Air Combat", "Air Defense", "Interception", "BVR Combat"],
    "Interceptor": ["Interception", "BVR Combat", "Air Defense"],
    "Multirole": ["Air Combat", "Air Defense", "Interception", "BVR Combat", "Electronic Warfare", "Strategic Reconnaissance"],
}
MISSION_TYPES = ["BVR Combat", "Air Combat", "Air Defense", "Interception", "Strategic Reconnaissance", "Electronic Warfare"]
WEATHER_OPTIONS = ["Clear", "Cloudy", "Rain"]
DISTANCE_OPTIONS = ["Short", "Medium", "Long"]


def missions_for(name):
    return ROLE_TO_MISSIONS.get(AIRCRAFT[name]["role"], [])


def run_mission(attacker, defender, mission, weather, distance):
    if mission == "BVR Combat":
        return ce.p_bvr(attacker, defender, weather, distance)
    if mission == "Air Combat":
        return ce.p_air_combat(attacker, defender, weather, distance)
    if mission == "Air Defense":
        return ce.p_air_defense(attacker, defender, weather, distance)
    if mission == "Interception":
        return ce.p_interception(attacker, defender, weather, distance)
    if mission == "Electronic Warfare":
        return ce.p_electronic_warfare(attacker, defender, weather, distance)
    if mission == "Strategic Reconnaissance":
        return ce.p_recon(attacker, weather, distance)
    return {"final": 0.0}


class SimulatorApp:
    def __init__(self, root):
        self.root = root
        root.title("OXCART - Air Combat Simulator")
        root.geometry("1180x720")
        root.configure(bg=BG)
        root.minsize(1080, 640)
        self._setup_style()

        self.country_var = tk.StringVar(value=next(iter(COUNTRIES)))
        self.mission_var = tk.StringVar(value=MISSION_TYPES[0])
        self.attacker_var = tk.StringVar()
        self.defender_var = tk.StringVar()
        self.weather_var = tk.StringVar(value="Clear")
        self.distance_var = tk.StringVar(value="Long")
        self.last_result = None

        self._build_layout()
        self._refresh_attacker_list()
        self._refresh_defender_list()

        for var in (self.country_var, self.mission_var):
            var.trace_add("write", lambda *a: self._refresh_attacker_list())
        self.attacker_var.trace_add("write", lambda *a: self._on_attacker_change())
        self.defender_var.trace_add("write", lambda *a: self._on_select_change())

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL, foreground=TEXT_DIM, padding=(18, 8), font=(FONT, 10))
        style.map("TNotebook.Tab", background=[("selected", PANEL_LIGHT)], foreground=[("selected", ACCENT)])
        style.configure("TCombobox", fieldbackground=PANEL_LIGHT, background=PANEL_LIGHT, foreground=TEXT, arrowcolor=ACCENT, borderwidth=0)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL_LIGHT)])

    def _build_layout(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=24, pady=(18, 6))
        tk.Label(header, text="AIR COMBAT SIMULATOR", bg=BG, fg=TEXT, font=(FONT, 18, "bold")).pack(side="left")
        tk.Label(header, text=f"  -  {CSV_PATH.name}  -  {len(AIRCRAFT)} aircraft", bg=BG, fg=TEXT_DIM, font=(FONT, 10)).pack(side="left", pady=(6, 0))

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=12)
        self._build_controls(body)
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(18, 0))
        self._build_result_card(right)
        self._build_tabs(right)

    def _control_combo(self, parent, label, var, values):
        tk.Label(parent, text=label, bg=PANEL, fg=TEXT_DIM, font=(FONT, 9, "bold")).pack(anchor="w", padx=16, pady=(12, 2))
        combo = ttk.Combobox(parent, textvariable=var, values=values, state="readonly", font=(FONT, 10), width=26)
        combo.pack(padx=16, fill="x")
        return combo

    def _build_controls(self, parent):
        panel = tk.Frame(parent, bg=PANEL, width=300)
        panel.pack(side="left", fill="y")
        panel.pack_propagate(False)
        tk.Label(panel, text="ENGAGEMENT SETUP", bg=PANEL, fg=ACCENT, font=(FONT, 10, "bold")).pack(anchor="w", padx=16, pady=(16, 4))
        self._control_combo(panel, "MISSION", self.mission_var, MISSION_TYPES)
        self._control_combo(panel, "ATTACKER COUNTRY", self.country_var, sorted(COUNTRIES.keys()))
        self.attacker_combo = self._control_combo(panel, "ATTACKER", self.attacker_var, [])
        self.defender_combo = self._control_combo(panel, "DEFENDER (enemy)", self.defender_var, sorted(AIRCRAFT.keys()))
        self._control_combo(panel, "WEATHER", self.weather_var, WEATHER_OPTIONS)
        self._control_combo(panel, "DISTANCE", self.distance_var, DISTANCE_OPTIONS)
        btn = tk.Button(panel, text="RUN SIMULATION", bg=ACCENT, fg="#0b0e14", activebackground=ACCENT_DIM, font=(FONT, 11, "bold"), relief="flat", cursor="hand2", command=self.simulate)
        btn.pack(fill="x", padx=16, pady=20, ipady=8)
        self.image_label = tk.Label(panel, bg=PANEL, fg=TEXT_DIM, text="(no image)", font=(FONT, 9))
        self.image_label.pack(pady=(4, 12))

    def _build_result_card(self, parent):
        card = tk.Frame(parent, bg=PANEL_LIGHT)
        card.pack(fill="x")
        self.prob_label = tk.Label(card, text="-", bg=PANEL_LIGHT, fg=ACCENT, font=(FONT, 40, "bold"))
        self.prob_label.pack(side="left", padx=24, pady=18)
        info = tk.Frame(card, bg=PANEL_LIGHT)
        info.pack(side="left", fill="both", expand=True, pady=18)
        self.result_title = tk.Label(info, text="Awaiting simulation", bg=PANEL_LIGHT, fg=TEXT, font=(FONT, 13, "bold"), anchor="w", justify="left")
        self.result_title.pack(anchor="w")
        self.result_detail = tk.Label(info, text="Configure an engagement and press Run.", bg=PANEL_LIGHT, fg=TEXT_DIM, font=(FONT, 10), anchor="w", justify="left", wraplength=520)
        self.result_detail.pack(anchor="w", pady=(4, 0))

    def _build_tabs(self, parent):
        self.tabs = ttk.Notebook(parent)
        self.tabs.pack(fill="both", expand=True, pady=(12, 0))
        self.fig_breakdown = Figure(figsize=(6, 3.2), dpi=100, facecolor=PANEL)
        self.fig_radar = Figure(figsize=(6, 3.2), dpi=100, facecolor=PANEL)
        self.fig_scatter = Figure(figsize=(6, 3.2), dpi=100, facecolor=PANEL)
        self.canvas_breakdown = self._add_tab(self.fig_breakdown, "Mission Breakdown")
        self.canvas_radar = self._add_tab(self.fig_radar, "Capability Radar")
        self.canvas_scatter = self._add_tab(self.fig_scatter, "Cost vs Capability")
        self._draw_scatter()

    def _add_tab(self, fig, title):
        frame = tk.Frame(self.tabs, bg=PANEL)
        self.tabs.add(frame, text=title)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        return canvas

    def _refresh_attacker_list(self):
        country = self.country_var.get()
        mission = self.mission_var.get()
        valid = [a for a in COUNTRIES.get(country, []) if mission in missions_for(a)]
        self.attacker_combo["values"] = valid
        if valid:
            if self.attacker_var.get() not in valid:
                self.attacker_var.set(valid[0])
        else:
            self.attacker_var.set("")

    def _refresh_defender_list(self):
        self.defender_combo["values"] = sorted(AIRCRAFT.keys())
        if not self.defender_var.get():
            self.defender_var.set("J-20 Mighty Dragon" if "J-20 Mighty Dragon" in AIRCRAFT else next(iter(AIRCRAFT)))

    def _on_attacker_change(self):
        self._update_image()
        self._on_select_change()

    def _on_select_change(self):
        if self.attacker_var.get() and self.defender_var.get():
            self._draw_radar()

    def _update_image(self):
        name = self.attacker_var.get()
        if not name:
            return
        key = name.lower().replace("-", "").replace(" ", "").replace("/", "")
        path = IMG_DIR / f"{key}.png"
        try:
            img = Image.open(path)
            img.thumbnail((240, 120), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo
        except Exception:
            self.image_label.configure(image="", text="(no image)")
            self.image_label.image = None

    def simulate(self):
        atk_name = self.attacker_var.get()
        if not atk_name:
            self._show_result(None, "No valid attacker", "Pick a mission this aircraft can fly.")
            return
        attacker = AIRCRAFT[atk_name]
        defender = AIRCRAFT[self.defender_var.get()]
        mission = self.mission_var.get()
        result = run_mission(attacker, defender, mission, self.weather_var.get(), self.distance_var.get())
        self.last_result = result
        final = result["final"]
        if mission == "Strategic Reconnaissance":
            detail = f"{atk_name} over contested airspace.  Engagement vs {defender['name']} not modeled for recon."
        else:
            detail = f"{atk_name}  vs  {defender['name']}   -   {mission}"
        self._show_result(final, mission, detail)
        self._draw_breakdown(result, mission)
        self._draw_radar()

    def _show_result(self, value, title, detail):
        if value is None:
            self.prob_label.config(text="-", fg=TEXT_DIM)
        else:
            color = GOOD if value >= 55 else WARN if value >= 25 else BAD
            self.prob_label.config(text=f"{value:.0f}%", fg=color)
        self.result_title.config(text=title)
        self.result_detail.config(text=detail)

    def _style_ax(self, ax, title):
        ax.set_facecolor(PANEL)
        ax.set_title(title, color=TEXT, fontsize=11, pad=10)
        ax.tick_params(colors=TEXT_DIM, labelsize=8)
        for spine in ax.spines.values():
            spine.set_color(PANEL_LIGHT)

    def _draw_breakdown(self, result, mission):
        self.fig_breakdown.clear()
        ax = self.fig_breakdown.add_subplot(111)
        self._style_ax(ax, f"{mission} - factor breakdown")
        factors = {k: v for k, v in result.items() if k != "final"}
        if not factors:
            ax.text(0.5, 0.5, "No sub-factors for this mission", color=TEXT_DIM, ha="center", transform=ax.transAxes)
        else:
            labels = [k.replace("_", " ").title() for k in factors]
            values = list(factors.values())
            colors = [GOOD if v >= 55 else WARN if v >= 25 else BAD for v in values]
            ax.barh(labels, values, color=colors)
            ax.set_xlim(0, 100)
            ax.set_xlabel("%", color=TEXT_DIM)
            for i, v in enumerate(values):
                ax.text(v + 1, i, f"{v:.0f}", color=TEXT, va="center", fontsize=8)
        self.fig_breakdown.tight_layout()
        self.canvas_breakdown.draw()

    def _draw_radar(self):
        self.fig_radar.clear()
        atk_name, def_name = self.attacker_var.get(), self.defender_var.get()
        if not atk_name or not def_name:
            return
        ax = self.fig_radar.add_subplot(111, polar=True)
        ax.set_facecolor(PANEL)
        ax.set_title("Capability comparison", color=TEXT, fontsize=11, pad=18)
        metrics = ["stealth", "maneuver", "radar", "missile", "ew", "speed"]
        labels = ["Stealth", "Maneuver", "Radar", "Missile", "EW", "Speed"]
        def vec(ac):
            return [ac["stealth"], ac["maneuver"], ac["radar"] / 10.0, ac["missile"], ac["ew"], min(1.0, ac["speed"] / 3000.0)]
        angles = [n / len(metrics) * 2 * math.pi for n in range(len(metrics))]
        angles += angles[:1]
        for name, color in [(atk_name, ACCENT), (def_name, BAD)]:
            v = vec(AIRCRAFT[name]) + vec(AIRCRAFT[name])[:1]
            ax.plot(angles, v, color=color, linewidth=2, label=name)
            ax.fill(angles, v, color=color, alpha=0.15)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, color=TEXT_DIM, fontsize=8)
        ax.set_yticklabels([])
        ax.set_ylim(0, 1)
        ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), facecolor=PANEL, edgecolor=PANEL_LIGHT, labelcolor=TEXT, fontsize=8)
        self.fig_radar.tight_layout()
        self.canvas_radar.draw()

    def _draw_scatter(self):
        self.fig_scatter.clear()
        ax = self.fig_scatter.add_subplot(111)
        self._style_ax(ax, "Unit cost vs composite capability")
        costs, caps, names = [], [], []
        for ac in AIRCRAFT.values():
            cap = (ac["stealth"] + ac["maneuver"] + ac["radar"] / 10.0 + ac["missile"] + ac["ew"]) / 5.0
            costs.append(ac["cost"])
            caps.append(cap * 100)
            names.append(ac["name"])
        gens = [AIRCRAFT[n]["generation"] for n in names]
        sc = ax.scatter(costs, caps, c=gens, cmap="viridis", s=40, alpha=0.85)
        ax.set_xlabel("Unit cost (M USD)", color=TEXT_DIM)
        ax.set_ylabel("Capability index", color=TEXT_DIM)
        cbar = self.fig_scatter.colorbar(sc, ax=ax)
        cbar.set_label("Generation", color=TEXT_DIM)
        cbar.ax.tick_params(colors=TEXT_DIM)
        self.fig_scatter.tight_layout()
        self.canvas_scatter.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = SimulatorApp(root)
    root.mainloop()
        "name": row["Aircraft"],
        "country": row["Country"],
        "generation": ce.parse_generation(row["Generation"]),
        "rcs": row["RCS_m2"],
        "radar": row["Radar_Score"] * 10,
        "missile": row["Missile_Score"],
        "ew": row["EW_Score"],
        "maneuver": min(1.0, row["Missile_Score"] + (0.1 if row["Thrust_Vectoring"] == "Yes" else 0)),
        "stealth": stealth_from_rcs(row["RCS_m2"]),
        "range": row["Combat_Radius_km"],
        "speed": row["Max_Speed_kmh"],
        "ceiling": row["Service_Ceiling_m"],
        "cost": row["Unit_Cost_M_USD"],
        "cost_hour": row["Cost_per_Flight_Hour_USD"],
        "role": row["Role"],
    }


CSV_PATH = resolve_csv_path()
DF = pd.read_csv(CSV_PATH)
AIRCRAFT = {row["Aircraft"]: build_aircraft(row) for _, row in DF.iterrows()}
COUNTRIES = {}
for ac in AIRCRAFT.values():
    COUNTRIES.setdefault(ac["country"], []).append(ac["name"])

ROLE_TO_MISSIONS = {
    "Air Superiority": ["Air Combat", "Air Defense", "Interception", "BVR Combat"],
    "Interceptor": ["Interception", "BVR Combat", "Air Defense"],
    "Multirole": ["Air Combat", "Air Defense", "Interception", "BVR Combat", "Electronic Warfare", "Strategic Reconnaissance"],
}
MISSION_TYPES = ["BVR Combat", "Air Combat", "Air Defense", "Interception", "Strategic Reconnaissance", "Electronic Warfare"]
WEATHER_OPTIONS = ["Clear", "Cloudy", "Rain"]
DISTANCE_OPTIONS = ["Short", "Medium", "Long"]


def missions_for(name):
    return ROLE_TO_MISSIONS.get(AIRCRAFT[name]["role"], [])


def run_mission(attacker, defender, mission, weather, distance):
    if mission == "BVR Combat":
        return ce.p_bvr(attacker, defender, weather, distance)
    if mission == "Air Combat":
        return ce.p_air_combat(attacker, defender, weather, distance)
    if mission == "Air Defense":
        return ce.p_air_defense(attacker, defender, weather, distance)
    if mission == "Interception":
        return ce.p_interception(attacker, defender, weather, distance)
    if mission == "Electronic Warfare":
        return ce.p_electronic_warfare(attacker, defender, weather, distance)
    if mission == "Strategic Reconnaissance":
        return ce.p_recon(attacker, weather, distance)
    return {"final": 0.0}


class SimulatorApp:
    def __init__(self, root):
        self.root = root
        root.title("OXCART - Air Combat Simulator")
        root.geometry("1180x720")
        root.configure(bg=BG)
        root.minsize(1080, 640)
        self._setup_style()

        self.country_var = tk.StringVar(value=next(iter(COUNTRIES)))
        self.mission_var = tk.StringVar(value=MISSION_TYPES[0])
        self.attacker_var = tk.StringVar()
        self.defender_var = tk.StringVar()
        self.weather_var = tk.StringVar(value="Clear")
        self.distance_var = tk.StringVar(value="Long")
        self.last_result = None

        self._build_layout()
        self._refresh_attacker_list()
        self._refresh_defender_list()

        for var in (self.country_var, self.mission_var):
            var.trace_add("write", lambda *a: self._refresh_attacker_list())
        self.attacker_var.trace_add("write", lambda *a: self._on_attacker_change())
        self.defender_var.trace_add("write", lambda *a: self._on_select_change())

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL, foreground=TEXT_DIM, padding=(18, 8), font=(FONT, 10))
        style.map("TNotebook.Tab", background=[("selected", PANEL_LIGHT)], foreground=[("selected", ACCENT)])
        style.configure("TCombobox", fieldbackground=PANEL_LIGHT, background=PANEL_LIGHT, foreground=TEXT, arrowcolor=ACCENT, borderwidth=0)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL_LIGHT)])

    def _build_layout(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=24, pady=(18, 6))
        tk.Label(header, text="AIR COMBAT SIMULATOR", bg=BG, fg=TEXT, font=(FONT, 18, "bold")).pack(side="left")
        tk.Label(header, text=f"  -  {CSV_PATH.name}  -  {len(AIRCRAFT)} aircraft", bg=BG, fg=TEXT_DIM, font=(FONT, 10)).pack(side="left", pady=(6, 0))

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=12)
        self._build_controls(body)
        right = tk.Frame(body, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(18, 0))
        self._build_result_card(right)
        self._build_tabs(right)

    def _control_combo(self, parent, label, var, values):
        tk.Label(parent, text=label, bg=PANEL, fg=TEXT_DIM, font=(FONT, 9, "bold")).pack(anchor="w", padx=16, pady=(12, 2))
        combo = ttk.Combobox(parent, textvariable=var, values=values, state="readonly", font=(FONT, 10), width=26)
        combo.pack(padx=16, fill="x")
        return combo

    def _build_controls(self, parent):
        panel = tk.Frame(parent, bg=PANEL, width=300)
        panel.pack(side="left", fill="y")
        panel.pack_propagate(False)
        tk.Label(panel, text="ENGAGEMENT SETUP", bg=PANEL, fg=ACCENT, font=(FONT, 10, "bold")).pack(anchor="w", padx=16, pady=(16, 4))
        self._control_combo(panel, "MISSION", self.mission_var, MISSION_TYPES)
        self._control_combo(panel, "ATTACKER COUNTRY", self.country_var, sorted(COUNTRIES.keys()))
        self.attacker_combo = self._control_combo(panel, "ATTACKER", self.attacker_var, [])
        self.defender_combo = self._control_combo(panel, "DEFENDER (enemy)", self.defender_var, sorted(AIRCRAFT.keys()))
        self._control_combo(panel, "WEATHER", self.weather_var, WEATHER_OPTIONS)
        self._control_combo(panel, "DISTANCE", self.distance_var, DISTANCE_OPTIONS)
        btn = tk.Button(panel, text="RUN SIMULATION", bg=ACCENT, fg="#0b0e14", activebackground=ACCENT_DIM, font=(FONT, 11, "bold"), relief="flat", cursor="hand2", command=self.simulate)
        btn.pack(fill="x", padx=16, pady=20, ipady=8)
        self.image_label = tk.Label(panel, bg=PANEL, fg=TEXT_DIM, text="(no image)", font=(FONT, 9))
        self.image_label.pack(pady=(4, 12))

    def _build_result_card(self, parent):
        card = tk.Frame(parent, bg=PANEL_LIGHT)
        card.pack(fill="x")
        self.prob_label = tk.Label(card, text="-", bg=PANEL_LIGHT, fg=ACCENT, font=(FONT, 40, "bold"))
        self.prob_label.pack(side="left", padx=24, pady=18)
        info = tk.Frame(card, bg=PANEL_LIGHT)
        info.pack(side="left", fill="both", expand=True, pady=18)
        self.result_title = tk.Label(info, text="Awaiting simulation", bg=PANEL_LIGHT, fg=TEXT, font=(FONT, 13, "bold"), anchor="w", justify="left")
        self.result_title.pack(anchor="w")
        self.result_detail = tk.Label(info, text="Configure an engagement and press Run.", bg=PANEL_LIGHT, fg=TEXT_DIM, font=(FONT, 10), anchor="w", justify="left", wraplength=520)
        self.result_detail.pack(anchor="w", pady=(4, 0))

    def _build_tabs(self, parent):
        self.tabs = ttk.Notebook(parent)
        self.tabs.pack(fill="both", expand=True, pady=(12, 0))
        self.fig_breakdown = Figure(figsize=(6, 3.2), dpi=100, facecolor=PANEL)
        self.fig_radar = Figure(figsize=(6, 3.2), dpi=100, facecolor=PANEL)
        self.fig_scatter = Figure(figsize=(6, 3.2), dpi=100, facecolor=PANEL)
        self.canvas_breakdown = self._add_tab(self.fig_breakdown, "Mission Breakdown")
        self.canvas_radar = self._add_tab(self.fig_radar, "Capability Radar")
        self.canvas_scatter = self._add_tab(self.fig_scatter, "Cost vs Capability")
        self._draw_scatter()

    def _add_tab(self, fig, title):
        frame = tk.Frame(self.tabs, bg=PANEL)
        self.tabs.add(frame, text=title)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        return canvas

    def _refresh_attacker_list(self):
        country = self.country_var.get()
        mission = self.mission_var.get()
        valid = [a for a in COUNTRIES.get(country, []) if mission in missions_for(a)]
        self.attacker_combo["values"] = valid
        if valid:
            if self.attacker_var.get() not in valid:
                self.attacker_var.set(valid[0])
        else:
            self.attacker_var.set("")

    def _refresh_defender_list(self):
        self.defender_combo["values"] = sorted(AIRCRAFT.keys())
        if not self.defender_var.get():
            self.defender_var.set("J-20 Mighty Dragon" if "J-20 Mighty Dragon" in AIRCRAFT else next(iter(AIRCRAFT)))

    def _on_attacker_change(self):
        self._update_image()
        self._on_select_change()

    def _on_select_change(self):
        if self.attacker_var.get() and self.defender_var.get():
            self._draw_radar()

    def _update_image(self):
        name = self.attacker_var.get()
        if not name:
            return
        key = name.lower().replace("-", "").replace(" ", "").replace("/", "")
        path = IMG_DIR / f"{key}.png"
        try:
            img = Image.open(path)
            img.thumbnail((240, 120), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo
        except Exception:
            self.image_label.configure(image="", text="(no image)")
            self.image_label.image = None

    def simulate(self):
        atk_name = self.attacker_var.get()
        if not atk_name:
            self._show_result(None, "No valid attacker", "Pick a mission this aircraft can fly.")
            return
        attacker = AIRCRAFT[atk_name]
        defender = AIRCRAFT[self.defender_var.get()]
        mission = self.mission_var.get()
        result = run_mission(attacker, defender, mission, self.weather_var.get(), self.distance_var.get())
        self.last_result = result
        final = result["final"]
        if mission == "Strategic Reconnaissance":
            detail = f"{atk_name} over contested airspace.  Engagement vs {defender['name']} not modeled for recon."
        else:
            detail = f"{atk_name}  vs  {defender['name']}   -   {mission}"
        self._show_result(final, mission, detail)
        self._draw_breakdown(result, mission)
        self._draw_radar()

    def _show_result(self, value, title, detail):
        if value is None:
            self.prob_label.config(text="-", fg=TEXT_DIM)
        else:
            color = GOOD if value >= 55 else WARN if value >= 25 else BAD
            self.prob_label.config(text=f"{value:.0f}%", fg=color)
        self.result_title.config(text=title)
        self.result_detail.config(text=detail)

    def _style_ax(self, ax, title):
        ax.set_facecolor(PANEL)
        ax.set_title(title, color=TEXT, fontsize=11, pad=10)
        ax.tick_params(colors=TEXT_DIM, labelsize=8)
        for spine in ax.spines.values():
            spine.set_color(PANEL_LIGHT)

    def _draw_breakdown(self, result, mission):
        self.fig_breakdown.clear()
        ax = self.fig_breakdown.add_subplot(111)
        self._style_ax(ax, f"{mission} - factor breakdown")
        factors = {k: v for k, v in result.items() if k != "final"}
        if not factors:
            ax.text(0.5, 0.5, "No sub-factors for this mission", color=TEXT_DIM, ha="center", transform=ax.transAxes)
        else:
            labels = [k.replace("_", " ").title() for k in factors]
            values = list(factors.values())
            colors = [GOOD if v >= 55 else WARN if v >= 25 else BAD for v in values]
            ax.barh(labels, values, color=colors)
            ax.set_xlim(0, 100)
            ax.set_xlabel("%", color=TEXT_DIM)
            for i, v in enumerate(values):
                ax.text(v + 1, i, f"{v:.0f}", color=TEXT, va="center", fontsize=8)
        self.fig_breakdown.tight_layout()
        self.canvas_breakdown.draw()

    def _draw_radar(self):
        self.fig_radar.clear()
        atk_name, def_name = self.attacker_var.get(), self.defender_var.get()
        if not atk_name or not def_name:
            return
        ax = self.fig_radar.add_subplot(111, polar=True)
        ax.set_facecolor(PANEL)
        ax.set_title("Capability comparison", color=TEXT, fontsize=11, pad=18)
        metrics = ["stealth", "maneuver", "radar", "missile", "ew", "speed"]
        labels = ["Stealth", "Maneuver", "Radar", "Missile", "EW", "Speed"]
        def vec(ac):
            return [ac["stealth"], ac["maneuver"], ac["radar"] / 10.0, ac["missile"], ac["ew"], min(1.0, ac["speed"] / 3000.0)]
        angles = [n / len(metrics) * 2 * math.pi for n in range(len(metrics))]
        angles += angles[:1]
        for name, color in [(atk_name, ACCENT), (def_name, BAD)]:
            v = vec(AIRCRAFT[name]) + vec(AIRCRAFT[name])[:1]
            ax.plot(angles, v, color=color, linewidth=2, label=name)
            ax.fill(angles, v, color=color, alpha=0.15)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, color=TEXT_DIM, fontsize=8)
        ax.set_yticklabels([])
        ax.set_ylim(0, 1)
        ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), facecolor=PANEL, edgecolor=PANEL_LIGHT, labelcolor=TEXT, fontsize=8)
        self.fig_radar.tight_layout()
        self.canvas_radar.draw()

    def _draw_scatter(self):
        self.fig_scatter.clear()
        ax = self.fig_scatter.add_subplot(111)
        self._style_ax(ax, "Unit cost vs composite capability")
        costs, caps, names = [], [], []
        for ac in AIRCRAFT.values():
            cap = (ac["stealth"] + ac["maneuver"] + ac["radar"] / 10.0 + ac["missile"] + ac["ew"]) / 5.0
            costs.append(ac["cost"])
            caps.append(cap * 100)
            names.append(ac["name"])
        gens = [AIRCRAFT[n]["generation"] for n in names]
        sc = ax.scatter(costs, caps, c=gens, cmap="viridis", s=40, alpha=0.85)
        ax.set_xlabel("Unit cost (M USD)", color=TEXT_DIM)
        ax.set_ylabel("Capability index", color=TEXT_DIM)
        cbar = self.fig_scatter.colorbar(sc, ax=ax)
        cbar.set_label("Generation", color=TEXT_DIM)
        cbar.ax.tick_params(colors=TEXT_DIM)
        self.fig_scatter.tight_layout()
        self.canvas_scatter.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = SimulatorApp(root)
    root.mainloop()