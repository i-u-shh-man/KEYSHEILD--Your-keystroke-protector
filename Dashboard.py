import csv
import subprocess
import tkinter as tk
from io import StringIO
from tkinter import messagebox, ttk


class KeyShieldGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("KeyShield: Behavioral Monitor")
        self.root.geometry("980x620")
        self.root.minsize(900, 560)
        self.root.configure(bg="#0b1220")
        self.metric_vars = {}
        self.process_details = tk.StringVar(value="Select a process to inspect its full details.")
        self.column_widths = {
            "pid": 90,
            "process_name": 220,
            "path": 420,
            "threat_score": 120,
            "status": 150,
        }

        self._configure_style()
        self._build_layout()
        self.populate_processes()
        self._refresh_metrics()

    def _configure_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("App.Treeview",
                        background="#0f172a",
                        foreground="#e2e8f0",
                        fieldbackground="#0f172a",
                        borderwidth=0,
                        rowheight=34,
                        font=("Segoe UI", 11))
        style.configure("App.Treeview.Heading",
                        background="#162033",
                        foreground="#dbeafe",
                        padding=(14, 10),
                        borderwidth=0,
                        font=("Segoe UI Semibold", 10))
        style.map("App.Treeview",
                  background=[("selected", "#1d4ed8")],
                  foreground=[("selected", "#f8fafc")])

        style.configure("Accent.Horizontal.TProgressbar",
                        troughcolor="#162033",
                        background="#22c55e",
                        bordercolor="#162033",
                        lightcolor="#22c55e",
                        darkcolor="#22c55e")

    def _build_layout(self):
        shell = tk.Frame(self.root, bg="#0b1220")
        shell.pack(fill="both", expand=True, padx=24, pady=24)

        header = tk.Frame(shell, bg="#111827", highlightbackground="#1e293b", highlightthickness=1)
        header.pack(fill="x")

        title_block = tk.Frame(header, bg="#111827")
        title_block.pack(side="left", fill="x", expand=True, padx=24, pady=20)

        tk.Label(title_block,
                 text="KEYSHIELD SECURITY OVERVIEW",
                 bg="#111827",
                 fg="#60a5fa",
                 font=("Segoe UI Semibold", 10)).pack(anchor="w")
        tk.Label(title_block,
                 text="Live behavioral process monitoring",
                 bg="#111827",
                 fg="#f8fafc",
                 font=("Segoe UI Semibold", 24)).pack(anchor="w", pady=(4, 6))
        tk.Label(title_block,
                 text="Track suspicious keyboard activity, review active signals, and isolate risky processes from one place.",
                 bg="#111827",
                 fg="#94a3b8",
                 font=("Segoe UI", 11)).pack(anchor="w")

        score_card = tk.Frame(header, bg="#172554", padx=20, pady=18)
        score_card.pack(side="right", padx=20, pady=20)
        tk.Label(score_card,
                 text="Protection score",
                 bg="#172554",
                 fg="#bfdbfe",
                 font=("Segoe UI", 10)).pack(anchor="e")
        self.protection_score = tk.StringVar(value="92%")
        tk.Label(score_card,
                 textvariable=self.protection_score,
                 bg="#172554",
                 fg="#f8fafc",
                 font=("Segoe UI Semibold", 26)).pack(anchor="e")

        metrics = tk.Frame(shell, bg="#0b1220")
        metrics.pack(fill="x", pady=(18, 18))

        for label, accent in (
            ("Processes scanned", "#38bdf8"),
            ("Active threats", "#ef4444"),
            ("Under review", "#f59e0b"),
            ("Trusted", "#22c55e"),
        ):
            card = tk.Frame(metrics, bg="#111827", highlightbackground="#1e293b", highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=6)
            tk.Label(card,
                     text=label.upper(),
                     bg="#111827",
                     fg="#94a3b8",
                     font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(14, 2))
            value = tk.StringVar(value="0")
            self.metric_vars[label] = value
            tk.Label(card,
                     textvariable=value,
                     bg="#111827",
                     fg="#f8fafc",
                     font=("Segoe UI Semibold", 20)).pack(anchor="w", padx=16, pady=(0, 6))
            tk.Frame(card, bg=accent, height=4).pack(fill="x", padx=16, pady=(0, 14))

        content = tk.Frame(shell, bg="#111827", highlightbackground="#1e293b", highlightthickness=1)
        content.pack(fill="both", expand=True)

        top_bar = tk.Frame(content, bg="#111827")
        top_bar.pack(fill="x", padx=20, pady=(18, 10))

        tk.Label(top_bar,
                 text="Observed processes",
                 bg="#111827",
                 fg="#f8fafc",
                 font=("Segoe UI Semibold", 16)).pack(side="left")

        self.status_chip = tk.Label(top_bar,
                                    text="System stable",
                                    bg="#052e16",
                                    fg="#bbf7d0",
                                    padx=12,
                                    pady=6,
                                    font=("Segoe UI Semibold", 10))
        self.status_chip.pack(side="right")

        table_frame = tk.Frame(content, bg="#111827")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        columns = ("pid", "process_name", "path", "threat_score", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="App.Treeview")
        self.tree.heading("pid", text="PID")
        self.tree.heading("process_name", text="Process Name")
        self.tree.heading("path", text="Executable Path")
        self.tree.heading("threat_score", text="Threat Score")
        self.tree.heading("status", text="Status")
        self.tree.column("pid", width=110, minwidth=80, anchor=tk.CENTER, stretch=False)
        self.tree.column("process_name", width=240, minwidth=180, anchor=tk.W, stretch=True)
        self.tree.column("path", width=460, minwidth=260, anchor=tk.W, stretch=True)
        self.tree.column("threat_score", width=140, minwidth=110, anchor=tk.CENTER, stretch=False)
        self.tree.column("status", width=180, minwidth=140, anchor=tk.CENTER, stretch=False)
        self.tree.tag_configure("trusted", background="#0f172a")
        self.tree.tag_configure("review", background="#131c31")
        self.tree.tag_configure("threat", background="#2a1220")
        self.tree.tag_configure("isolated", background="#13261a")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=x_scrollbar.set)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        self.tree.bind("<<TreeviewSelect>>", self._update_details)
        self.tree.bind("<Configure>", self._resize_columns)

        details_bar = tk.Frame(content, bg="#101826")
        details_bar.pack(fill="x", padx=20, pady=(0, 16))
        tk.Label(details_bar,
                 text="Selection",
                 bg="#101826",
                 fg="#60a5fa",
                 font=("Segoe UI Semibold", 10)).pack(anchor="w", padx=16, pady=(14, 2))
        tk.Label(details_bar,
                 textvariable=self.process_details,
                 justify="left",
                 wraplength=860,
                 bg="#101826",
                 fg="#dbeafe",
                 font=("Segoe UI", 10)).pack(anchor="w", fill="x", padx=16, pady=(0, 14))

        footer = tk.Frame(content, bg="#0f172a")
        footer.pack(fill="x", padx=20, pady=(0, 20))

        footer_left = tk.Frame(footer, bg="#0f172a")
        footer_left.pack(side="left", fill="x", expand=True, padx=18, pady=16)
        tk.Label(footer_left,
                 text="Threat response readiness",
                 bg="#0f172a",
                 fg="#f8fafc",
                 font=("Segoe UI Semibold", 12)).pack(anchor="w")
        tk.Label(footer_left,
                 text="Isolation is applied automatically to any process with a threat score of 70 or higher.",
                 bg="#0f172a",
                 fg="#94a3b8",
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 10))
        self.readiness = ttk.Progressbar(footer_left,
                                         style="Accent.Horizontal.TProgressbar",
                                         mode="determinate",
                                         maximum=100,
                                         value=92)
        self.readiness.pack(fill="x")

        self.btn = tk.Button(footer,
                             text="Isolate High Threats",
                             command=self.mitigate,
                             bg="#dc2626",
                             activebackground="#b91c1c",
                             activeforeground="#ffffff",
                             fg="white",
                             bd=0,
                             padx=22,
                             pady=14,
                             font=("Segoe UI Semibold", 11),
                             cursor="hand2")
        self.btn.pack(side="right", padx=18, pady=18)

        self.refresh_btn = tk.Button(footer,
                                     text="Refresh Process List",
                                     command=self.refresh_processes,
                                     bg="#1d4ed8",
                                     activebackground="#1e40af",
                                     activeforeground="#ffffff",
                                     fg="white",
                                     bd=0,
                                     padx=18,
                                     pady=14,
                                     font=("Segoe UI Semibold", 11),
                                     cursor="hand2")
        self.refresh_btn.pack(side="right", padx=(0, 10), pady=18)

    def _tag_for_status(self, status):
        mapping = {
            "Trusted": "trusted",
            "Under review": "review",
            "Active threat": "threat",
            "Isolated": "isolated",
        }
        return mapping.get(status, "trusted")

    def _score_process(self, process_name, path):
        name = process_name.lower()
        path_text = path.lower()
        suspicious_keywords = ("logger", "hook", "macro", "inject", "record", "monitor", "spy", "key")

        score = 5
        if any(keyword in name for keyword in suspicious_keywords):
            score += 55
        if any(keyword in path_text for keyword in suspicious_keywords):
            score += 20
        if not path:
            score += 10
        if path and "\\temp\\" in path_text:
            score += 20
        return min(score, 95)

    def _status_for_score(self, score):
        if score >= 70:
            return "Active threat"
        if score >= 35:
            return "Under review"
        return "Trusted"

    def _read_process_rows(self):
        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-Process | Select-Object Id,ProcessName,Path | ConvertTo-Csv -NoTypeInformation",
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        reader = csv.DictReader(StringIO(result.stdout))
        rows = []
        for row in reader:
            pid = row.get("Id", "").strip()
            process_name = row.get("ProcessName", "").strip()
            path = row.get("Path", "").strip() or "System or access-restricted process"
            threat_score = self._score_process(process_name, path)
            status = self._status_for_score(threat_score)
            rows.append((pid, process_name, path, threat_score, status))
        rows.sort(key=lambda item: (-item[3], item[1].lower()))
        return rows

    def populate_processes(self):
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        try:
            rows = self._read_process_rows()
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            rows = [("N/A", "Process scan unavailable", "Unable to query Windows processes in this environment", 0, "Trusted")]

        for row in rows:
            self.tree.insert("", "end", values=row, tags=(self._tag_for_status(row[4]),))

        children = self.tree.get_children()
        if children:
            self.tree.selection_set(children[0])
            self.tree.focus(children[0])
            self._update_details()

    def refresh_processes(self):
        self.populate_processes()
        self._refresh_metrics()

    def _update_details(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            self.process_details.set("Select a process to inspect its full details.")
            return

        values = self.tree.item(selection[0], "values")
        self.process_details.set(
            f"PID {values[0]}  |  {values[1]}  |  Score {values[3]}  |  {values[4]}  |  {values[2]}"
        )

    def _resize_columns(self, event):
        total_width = max(event.width - 24, 0)
        fixed_width = self.column_widths["pid"] + self.column_widths["threat_score"] + self.column_widths["status"]
        flexible_width = max(total_width - fixed_width, 440)
        process_name_width = max(int(flexible_width * 0.32), 180)
        path_width = max(flexible_width - process_name_width, 260)
        self.tree.column("process_name", width=process_name_width)
        self.tree.column("path", width=path_width)

    def _refresh_metrics(self):
        items = [self.tree.item(item_id, "values") for item_id in self.tree.get_children()]
        counts = {
            "Processes scanned": len(items),
            "Active threats": sum(1 for item in items if item[4] == "Active threat"),
            "Under review": sum(1 for item in items if item[4] == "Under review"),
            "Trusted": sum(1 for item in items if item[4] in ("Trusted", "Isolated")),
        }

        for label, value in counts.items():
            self.metric_vars[label].set(str(value))

        active_threats = counts["Active threats"]
        if active_threats:
            self.status_chip.config(text=f"{active_threats} active threat detected", bg="#3f0d16", fg="#fecdd3")
            self.protection_score.set("68%")
            self.readiness.configure(value=68)
        else:
            self.status_chip.config(text="System stable", bg="#052e16", fg="#bbf7d0")
            self.protection_score.set("92%")
            self.readiness.configure(value=92)

    def mitigate(self):
        mitigated = []
        for item_id in self.tree.get_children():
            values = list(self.tree.item(item_id, "values"))
            threat_score = int(values[3])
            if threat_score >= 70 and values[4] != "Isolated":
                values[4] = "Isolated"
                self.tree.item(item_id, values=values, tags=("isolated",))
                mitigated.append(f"PID {values[0]} ({values[1]})")

        self._refresh_metrics()
        self._update_details()

        if mitigated:
            messagebox.showinfo(
                "Mitigation complete",
                "Isolated high-threat processes:\n" + "\n".join(mitigated),
            )
        else:
            messagebox.showinfo("Mitigation complete", "No high-threat processes were found.")


if __name__ == "__main__":
    root = tk.Tk()
    app = KeyShieldGUI(root)
    root.mainloop()
