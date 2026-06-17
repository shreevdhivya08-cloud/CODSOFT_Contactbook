"""
Reusable custom widgets for ContactBook.
"""

import tkinter as tk
import customtkinter as ctk
from .theme import FONTS, CORNER_RADIUS


class LabeledEntry(ctk.CTkFrame):
    """A label + CTkEntry stacked vertically."""

    def __init__(self, parent, label: str, placeholder: str = "", **kwargs):
        super().__init__(parent, fg_color="transparent")
        self._label = ctk.CTkLabel(self, text=label, font=FONTS["small_bold"],
                                    anchor="w")
        self._label.pack(fill="x", pady=(0, 2))
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder,
                                   corner_radius=CORNER_RADIUS, **kwargs)
        self.entry.pack(fill="x")

    def get(self) -> str:
        return self.entry.get()

    def set(self, value: str) -> None:
        self.entry.delete(0, "end")
        self.entry.insert(0, value)

    def clear(self) -> None:
        self.entry.delete(0, "end")

    def configure_entry(self, **kwargs):
        self.entry.configure(**kwargs)


class LabeledTextbox(ctk.CTkFrame):
    """A label + CTkTextbox stacked vertically."""

    def __init__(self, parent, label: str, height: int = 80, **kwargs):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text=label, font=FONTS["small_bold"],
                     anchor="w").pack(fill="x", pady=(0, 2))
        self.textbox = ctk.CTkTextbox(self, height=height,
                                       corner_radius=CORNER_RADIUS, **kwargs)
        self.textbox.pack(fill="x")

    def get(self) -> str:
        return self.textbox.get("1.0", "end").strip()

    def set(self, value: str) -> None:
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", value)

    def clear(self) -> None:
        self.textbox.delete("1.0", "end")


class StatCard(ctk.CTkFrame):
    """A mini dashboard card showing a number + label."""

    def __init__(self, parent, label: str, value: str = "0",
                 accent_color: str = "#7C6EFA", **kwargs):
        super().__init__(parent, corner_radius=CORNER_RADIUS, **kwargs)
        self._number_var = tk.StringVar(value=value)
        self._number_lbl = ctk.CTkLabel(self, textvariable=self._number_var,
                                         font=FONTS["stat_number"],
                                         text_color=accent_color)
        self._number_lbl.pack(pady=(12, 0))
        ctk.CTkLabel(self, text=label, font=FONTS["stat_label"],
                     text_color="gray").pack(pady=(0, 12))

    def update_value(self, value: str | int) -> None:
        self._number_var.set(str(value))


class NavButton(ctk.CTkButton):
    """Sidebar navigation button with active-state toggle."""

    def __init__(self, parent, text: str, command=None, icon: str = "", **kwargs):
        label = f"  {icon}  {text}" if icon else f"  {text}"
        super().__init__(
            parent,
            text=label,
            anchor="w",
            corner_radius=8,
            height=40,
            border_spacing=6,
            font=FONTS["nav"],
            command=command,
            **kwargs,
        )
        self._active = False

    def set_active(self, active: bool, active_color: str, inactive_color: str,
                   text_active: str, text_inactive: str) -> None:
        self._active = active
        self.configure(
            fg_color=active_color if active else inactive_color,
            text_color=text_active if active else text_inactive,
        )


class ToastNotification(ctk.CTkToplevel):
    """Transient toast message that auto-dismisses after *ms* milliseconds."""

    def __init__(self, parent, message: str, kind: str = "info", ms: int = 2800):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        colors = {"info": "#7C6EFA", "success": "#4ECDC4",
                  "error": "#FF6B6B", "warning": "#FFD93D"}
        fg = colors.get(kind, colors["info"])

        frame = ctk.CTkFrame(self, fg_color=fg, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=0, pady=0)
        ctk.CTkLabel(frame, text=message, font=FONTS["body"],
                     text_color="#FFFFFF", wraplength=280).pack(
            padx=16, pady=12
        )

        # Position near the bottom-right of the parent window
        parent.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width()  - 320
        py = parent.winfo_rooty() + parent.winfo_height() - 80
        self.geometry(f"300x54+{px}+{py}")
        self.after(ms, self.destroy)


class ConfirmDialog(ctk.CTkToplevel):
    """Modal yes/no confirmation dialog. Sets self.result = True/False."""

    def __init__(self, parent, title: str, message: str):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.result = False

        self.geometry("360x160")
        ctk.CTkLabel(self, text=message, font=FONTS["body"],
                     wraplength=320).pack(padx=20, pady=(24, 16))
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack()
        ctk.CTkButton(btn_row, text="Cancel", width=100,
                      fg_color="gray30",
                      command=self._cancel).pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="Delete", width=100,
                      fg_color="#FF6B6B", hover_color="#FF4444",
                      command=self._confirm).pack(side="left", padx=6)
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _confirm(self):
        self.result = True
        self.destroy()

    def _cancel(self):
        self.result = False
        self.destroy()
