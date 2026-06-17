"""
Contact Form Dialog — used for both adding and editing contacts.
"""

import customtkinter as ctk
from .theme import FONTS, CORNER_RADIUS, PAD
from .widgets import LabeledEntry, LabeledTextbox


class ContactFormDialog(ctk.CTkToplevel):
    """
    Modal dialog for adding or editing a contact.

    On close, check `self.result` for the submitted data dict,
    or None if the user cancelled.
    """

    def __init__(self, parent, title: str = "Add Contact",
                 contact_data: dict | None = None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.result: dict | None = None
        self._contact_data = contact_data or {}

        self.geometry("460x620")
        self._build_ui()
        self._populate(self._contact_data)
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Header
        header = ctk.CTkFrame(self, height=56, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text=self.title(),
                     font=FONTS["section"]).pack(side="left", padx=PAD)

        # Scrollable body
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=PAD, pady=PAD)
        scroll.columnconfigure(0, weight=1)

        def row(widget_class, *args, **kw):
            w = widget_class(scroll, *args, **kw)
            w.pack(fill="x", pady=(0, 10))
            return w

        self._name    = row(LabeledEntry, "Full Name *",    "Jane Doe")
        self._phone   = row(LabeledEntry, "Phone Number *", "+1 234 567 8900")
        self._email   = row(LabeledEntry, "Email Address",  "jane@example.com")
        self._company = row(LabeledEntry, "Company",        "Acme Corp")
        self._address = row(LabeledEntry, "Address",        "123 Main St, City")
        self._notes   = row(LabeledTextbox, "Notes", height=80)

        # Favourite toggle
        fav_row = ctk.CTkFrame(scroll, fg_color="transparent")
        fav_row.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(fav_row, text="★  Mark as Favourite",
                     font=FONTS["body"]).pack(side="left")
        self._fav_var = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(fav_row, text="", variable=self._fav_var,
                      width=46).pack(side="right")

        # Error label
        self._error_var = ctk.StringVar()
        ctk.CTkLabel(scroll, textvariable=self._error_var,
                     font=FONTS["small"], text_color="#FF6B6B",
                     wraplength=400).pack(fill="x", pady=(0, 4))

        # Footer buttons
        footer = ctk.CTkFrame(self, height=60, corner_radius=0)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        ctk.CTkButton(footer, text="Cancel", width=110,
                      fg_color="gray30",
                      command=self._cancel).pack(side="right", padx=8, pady=10)
        ctk.CTkButton(footer, text="Save Contact", width=130,
                      command=self._submit).pack(side="right", padx=0, pady=10)

    # ── Data helpers ──────────────────────────────────────────────────────────

    def _populate(self, data: dict) -> None:
        if not data:
            return
        self._name.set(data.get("full_name", ""))
        self._phone.set(data.get("phone", ""))
        self._email.set(data.get("email", ""))
        self._company.set(data.get("company", ""))
        self._address.set(data.get("address", ""))
        self._notes.set(data.get("notes", ""))
        self._fav_var.set(bool(data.get("favorite", False)))

    def _collect(self) -> dict:
        return {
            "full_name": self._name.get().strip(),
            "phone":     self._phone.get().strip(),
            "email":     self._email.get().strip(),
            "company":   self._company.get().strip(),
            "address":   self._address.get().strip(),
            "notes":     self._notes.get().strip(),
            "favorite":  self._fav_var.get(),
        }

    # ── Actions ───────────────────────────────────────────────────────────────

    def _submit(self) -> None:
        data = self._collect()
        # Basic required-field check (full validation happens in db layer)
        if not data["full_name"]:
            self._error_var.set("Full Name is required.")
            return
        if not data["phone"]:
            self._error_var.set("Phone Number is required.")
            return
        self._error_var.set("")
        self.result = data
        self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()
