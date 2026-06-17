"""
ContactBook — Main Application Window
Built with CustomTkinter · SQLite · OOP architecture
"""

from __future__ import annotations

import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
from tkinter import filedialog, messagebox

from database import DatabaseManager
from .theme  import COLORS, FONTS, SIDEBAR_WIDTH, DETAIL_WIDTH, PAD, CORNER_RADIUS
from .widgets import StatCard, NavButton, ToastNotification, ConfirmDialog
from .contact_form import ContactFormDialog


# ──────────────────────────────────────────────────────────────────────────────
# App
# ──────────────────────────────────────────────────────────────────────────────

class ContactBookApp(ctk.CTk):
    """Root application window."""

    APP_TITLE   = "ContactBook"
    MIN_W, MIN_H = 1100, 680
    DEFAULT_MODE = "dark"

    def __init__(self):
        super().__init__()
        # ── state ──────────────────────────────────────────────────────────────
        self._mode          : str        = self.DEFAULT_MODE
        self._selected_id   : int | None = None
        self._current_view  : str        = "all"   # "all" | "favorites"
        self._db            = DatabaseManager()
        self._colors        = COLORS[self._mode]
        self._nav_buttons   : dict[str, NavButton] = {}

        # ── window ─────────────────────────────────────────────────────────────
        self.title(self.APP_TITLE)
        self.minsize(self.MIN_W, self.MIN_H)
        self.geometry(f"{self.MIN_W}x{self.MIN_H}")
        ctk.set_appearance_mode(self._mode)
        ctk.set_default_color_theme("blue")

        self._apply_ttk_style()
        self._build_layout()
        self._refresh_all()

    # ══════════════════════════════════════════════════════════════════════════
    # Layout builders
    # ══════════════════════════════════════════════════════════════════════════

    def _build_layout(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._sidebar = self._build_sidebar()
        self._sidebar.grid(row=0, column=0, sticky="nsew")

        main = ctk.CTkFrame(self, fg_color=self._colors["bg_primary"],
                             corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(1, weight=1)

        self._build_topbar(main)

        body = ctk.CTkFrame(main, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        self._build_dashboard(body)
        self._build_contact_list(body)
        self._detail_panel = self._build_detail_panel(body)

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self) -> ctk.CTkFrame:
        c = self._colors
        sidebar = ctk.CTkFrame(self, width=SIDEBAR_WIDTH, corner_radius=0,
                                fg_color=c["bg_secondary"])
        sidebar.pack_propagate(False)

        # Logo / title
        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent", height=72)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        ctk.CTkLabel(title_frame, text="◉  ContactBook",
                     font=FONTS["app_title"],
                     text_color=c["accent"]).pack(padx=PAD, pady=16, anchor="w")

        ctk.CTkFrame(sidebar, height=1, fg_color=c["separator"]).pack(fill="x")

        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", pady=8, padx=8)

        nav_items = [
            ("all",       "👥", "All Contacts"),
            ("favorites", "★",  "Favourites"),
        ]
        for key, icon, label in nav_items:
            btn = NavButton(
                nav_frame, text=label, icon=icon,
                fg_color="transparent",
                text_color=c["text_secondary"],
                hover_color=c["bg_hover"],
                command=lambda k=key: self._switch_view(k),
            )
            btn.pack(fill="x", pady=2)
            self._nav_buttons[key] = btn

        ctk.CTkFrame(sidebar, height=1, fg_color=c["separator"]).pack(fill="x", pady=8)

        # Action buttons
        action_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        action_frame.pack(fill="x", padx=8)
        for text, cmd in [
            ("＋  Add Contact",   self._on_add),
            ("⬆  Export CSV",    self._on_export),
            ("⬇  Import CSV",    self._on_import),
        ]:
            ctk.CTkButton(action_frame, text=text, anchor="w",
                          height=36, corner_radius=8,
                          font=FONTS["small_bold"],
                          fg_color=c["accent"], hover_color=c["accent_hover"],
                          command=cmd).pack(fill="x", pady=3)

        # Spacer
        ctk.CTkFrame(sidebar, fg_color="transparent").pack(fill="both", expand=True)

        # Theme toggle at the bottom
        bottom = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom.pack(fill="x", padx=PAD, pady=PAD)
        ctk.CTkLabel(bottom, text="Dark mode", font=FONTS["small"],
                     text_color=c["text_secondary"]).pack(side="left")
        self._theme_switch = ctk.CTkSwitch(
            bottom, text="", width=46,
            command=self._toggle_theme,
        )
        self._theme_switch.select()   # default = dark
        self._theme_switch.pack(side="right")

        return sidebar

    # ── Top bar ───────────────────────────────────────────────────────────────

    def _build_topbar(self, parent: ctk.CTkFrame) -> None:
        c = self._colors
        bar = ctk.CTkFrame(parent, height=60, fg_color=c["bg_secondary"],
                            corner_radius=0)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.columnconfigure(0, weight=1)

        self._view_title = ctk.CTkLabel(bar, text="All Contacts",
                                         font=FONTS["section"],
                                         anchor="w")
        self._view_title.grid(row=0, column=0, padx=PAD, sticky="w")

        # Search bar
        search_frame = ctk.CTkFrame(bar, fg_color="transparent")
        search_frame.grid(row=0, column=1, padx=PAD, pady=8, sticky="e")

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._on_search())
        self._search_entry = ctk.CTkEntry(
            search_frame, textvariable=self._search_var,
            placeholder_text="🔍  Search name, phone, email…",
            width=280, corner_radius=CORNER_RADIUS,
            font=FONTS["input"],
        )
        self._search_entry.pack(side="left", padx=(0, 6))
        ctk.CTkButton(search_frame, text="✕", width=32, height=32,
                       corner_radius=8, fg_color="gray30",
                       command=self._clear_search).pack(side="left")

    # ── Dashboard stat cards ──────────────────────────────────────────────────

    def _build_dashboard(self, parent: ctk.CTkFrame) -> None:
        c = self._colors
        dash = ctk.CTkFrame(parent, fg_color="transparent")
        dash.grid(row=0, column=0, columnspan=2, sticky="ew", padx=PAD, pady=(PAD, 0))
        for i in range(4):
            dash.columnconfigure(i, weight=1)

        defs = [
            ("Total",      "total",      c["accent"]),
            ("Favourites", "favorites",  c["star"]),
            ("With Email", "with_email", c["success"]),
            ("Companies",  "companies",  c["warning"]),
        ]
        self._stat_cards: dict[str, StatCard] = {}
        for col, (label, key, color) in enumerate(defs):
            card = StatCard(dash, label=label, accent_color=color,
                            fg_color=c["bg_secondary"])
            card.grid(row=0, column=col, padx=4, pady=(0, PAD), sticky="ew")
            self._stat_cards[key] = card

    # ── Contact list (treeview) ───────────────────────────────────────────────

    def _build_contact_list(self, parent: ctk.CTkFrame) -> None:
        c = self._colors
        list_frame = ctk.CTkFrame(parent, fg_color=c["bg_secondary"],
                                   corner_radius=CORNER_RADIUS)
        list_frame.grid(row=1, column=0, sticky="nsew",
                        padx=(PAD, 4), pady=(0, PAD))
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

        # Column definitions
        columns = ("fav", "name", "phone", "email", "company")
        col_cfg = {
            "fav":     ("★",       44),
            "name":    ("Name",    200),
            "phone":   ("Phone",   150),
            "email":   ("Email",   200),
            "company": ("Company", 140),
        }

        self._tree = ttk.Treeview(
            list_frame, columns=columns, show="headings",
            style="ContactBook.Treeview",
        )
        for col, (heading, width) in col_cfg.items():
            self._tree.heading(col, text=heading,
                               command=lambda c=col: self._sort_tree(c))
            self._tree.column(col, width=width, minwidth=40,
                              anchor="center" if col == "fav" else "w")

        vsb = ttk.Scrollbar(list_frame, orient="vertical",
                             command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)

        self._tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        vsb.pack(side="right", fill="y", pady=2)

        self._tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self._tree.bind("<Double-1>",         self._on_edit)
        self._tree.bind("<Delete>",           self._on_delete)

        # Context menu
        self._ctx_menu = tk.Menu(self, tearoff=0)
        self._ctx_menu.add_command(label="✏  Edit",             command=self._on_edit)
        self._ctx_menu.add_command(label="★  Toggle Favourite", command=self._on_toggle_fav)
        self._ctx_menu.add_separator()
        self._ctx_menu.add_command(label="🗑  Delete",          command=self._on_delete)
        self._tree.bind("<Button-3>", self._show_context_menu)

    # ── Detail panel ─────────────────────────────────────────────────────────

    def _build_detail_panel(self, parent: ctk.CTkFrame) -> ctk.CTkFrame:
        c = self._colors
        panel = ctk.CTkFrame(parent, width=DETAIL_WIDTH,
                              fg_color=c["bg_secondary"],
                              corner_radius=CORNER_RADIUS)
        panel.grid(row=1, column=1, sticky="nsew",
                   padx=(4, PAD), pady=(0, PAD))
        panel.grid_propagate(False)
        parent.columnconfigure(1, minsize=DETAIL_WIDTH)

        # Avatar
        av_frame = ctk.CTkFrame(panel, fg_color="transparent")
        av_frame.pack(pady=(PAD*2, 0))
        self._avatar_lbl = ctk.CTkLabel(
            av_frame, text="?", width=80, height=80,
            corner_radius=40,
            fg_color=c["accent_dim"],
            font=("Segoe UI", 30, "bold"),
        )
        self._avatar_lbl.pack()

        self._detail_name = ctk.CTkLabel(panel, text="Select a contact",
                                          font=FONTS["section"])
        self._detail_name.pack(pady=(8, 2))
        self._detail_company = ctk.CTkLabel(panel, text="",
                                             font=FONTS["small"],
                                             text_color="gray")
        self._detail_company.pack()

        ctk.CTkFrame(panel, height=1, fg_color=c["separator"]).pack(
            fill="x", padx=PAD, pady=PAD
        )

        # Detail fields
        fields_frame = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=PAD)

        self._detail_fields: dict[str, ctk.CTkLabel] = {}
        for icon, key, label in [
            ("📞", "phone",   "Phone"),
            ("✉",  "email",   "Email"),
            ("🏠", "address", "Address"),
            ("📝", "notes",   "Notes"),
        ]:
            row_f = ctk.CTkFrame(fields_frame, fg_color="transparent")
            row_f.pack(fill="x", pady=3)
            ctk.CTkLabel(row_f, text=f"{icon}  {label}",
                         font=FONTS["small_bold"], width=90,
                         anchor="w").pack(side="left")
            val = ctk.CTkLabel(row_f, text="—", font=FONTS["small"],
                               anchor="w", wraplength=180, justify="left")
            val.pack(side="left", fill="x", expand=True)
            self._detail_fields[key] = val

        # Action buttons inside detail panel
        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.pack(fill="x", padx=PAD, pady=PAD)
        self._edit_btn = ctk.CTkButton(btn_row, text="✏  Edit", width=100,
                                        fg_color=c["accent"],
                                        hover_color=c["accent_hover"],
                                        command=self._on_edit, state="disabled")
        self._edit_btn.pack(side="left", padx=(0, 6))
        self._del_btn = ctk.CTkButton(btn_row, text="🗑  Delete", width=100,
                                       fg_color=c["danger"],
                                       hover_color="#FF4444",
                                       command=self._on_delete, state="disabled")
        self._del_btn.pack(side="left")
        self._fav_btn = ctk.CTkButton(btn_row, text="★", width=40,
                                       fg_color="gray30",
                                       command=self._on_toggle_fav,
                                       state="disabled")
        self._fav_btn.pack(side="right")

        return panel

    # ══════════════════════════════════════════════════════════════════════════
    # Data loading / display
    # ══════════════════════════════════════════════════════════════════════════

    def _refresh_all(self) -> None:
        """Reload stats and contact list from the database."""
        self._refresh_stats()
        self._load_contacts()

    def _refresh_stats(self) -> None:
        stats = self._db.get_stats()
        for key, card in self._stat_cards.items():
            card.update_value(stats.get(key, 0))

    def _load_contacts(self, contacts: list[dict] | None = None) -> None:
        """Populate the treeview. If *contacts* is None, loads from DB."""
        if contacts is None:
            if self._current_view == "favorites":
                contacts = self._db.get_all_contacts(favorites_only=True)
            else:
                contacts = self._db.get_all_contacts()

        # Remember selection
        sel_id = self._selected_id

        for item in self._tree.get_children():
            self._tree.delete(item)

        c = self._colors
        for i, contact in enumerate(contacts):
            fav  = "★" if contact.get("favorite") else ""
            tags = ("even",) if i % 2 == 0 else ("odd",)
            if contact.get("favorite"):
                tags = tags + ("fav",)
            iid = str(contact["id"])
            self._tree.insert(
                "", "end", iid=iid, tags=tags,
                values=(
                    fav,
                    contact.get("full_name", ""),
                    contact.get("phone",     ""),
                    contact.get("email",     ""),
                    contact.get("company",   ""),
                ),
            )

        # Re-apply tag colours (must be after inserts)
        self._tree.tag_configure("odd",  background=c["table_row_odd"])
        self._tree.tag_configure("even", background=c["table_row_even"])
        self._tree.tag_configure("fav",  foreground=c["star"])

        # Restore selection if contact still exists
        if sel_id and self._tree.exists(str(sel_id)):
            self._tree.selection_set(str(sel_id))
            self._tree.see(str(sel_id))
        else:
            self._clear_detail()

    def _populate_detail(self, contact: dict) -> None:
        """Render contact details in the right panel."""
        name    = contact.get("full_name", "?")
        initials = "".join(p[0].upper() for p in name.split()[:2]) or "?"
        self._avatar_lbl.configure(text=initials)
        self._detail_name.configure(text=name)
        self._detail_company.configure(text=contact.get("company", ""))
        for key, lbl in self._detail_fields.items():
            lbl.configure(text=contact.get(key, "") or "—")
        # Buttons
        for btn in (self._edit_btn, self._del_btn, self._fav_btn):
            btn.configure(state="normal")
        fav_icon = "★" if contact.get("favorite") else "☆"
        self._fav_btn.configure(text=fav_icon)

    def _clear_detail(self) -> None:
        self._selected_id = None
        self._avatar_lbl.configure(text="?")
        self._detail_name.configure(text="Select a contact")
        self._detail_company.configure(text="")
        for lbl in self._detail_fields.values():
            lbl.configure(text="—")
        for btn in (self._edit_btn, self._del_btn, self._fav_btn):
            btn.configure(state="disabled")

    # ══════════════════════════════════════════════════════════════════════════
    # Event handlers
    # ══════════════════════════════════════════════════════════════════════════

    def _on_tree_select(self, _event=None) -> None:
        sel = self._tree.selection()
        if not sel:
            self._clear_detail()
            return
        contact_id       = int(sel[0])
        self._selected_id = contact_id
        contact          = self._db.get_contact_by_id(contact_id)
        if contact:
            self._populate_detail(contact)

    def _on_add(self) -> None:
        dlg = ContactFormDialog(self, title="Add Contact")
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            new_id = self._db.add_contact(**dlg.result)
            self._selected_id = new_id
            self._refresh_all()
            self._toast("Contact added.", "success")
        except ValueError as exc:
            self._toast(str(exc), "error")

    def _on_edit(self, _event=None) -> None:
        if not self._selected_id:
            return
        contact = self._db.get_contact_by_id(self._selected_id)
        if not contact:
            return
        dlg = ContactFormDialog(self, title="Edit Contact", contact_data=contact)
        self.wait_window(dlg)
        if dlg.result is None:
            return
        try:
            self._db.update_contact(self._selected_id, **dlg.result)
            self._refresh_all()
            self._toast("Contact updated.", "success")
        except ValueError as exc:
            self._toast(str(exc), "error")

    def _on_delete(self, _event=None) -> None:
        if not self._selected_id:
            return
        contact = self._db.get_contact_by_id(self._selected_id)
        name    = contact.get("full_name", "this contact") if contact else "this contact"
        dlg     = ConfirmDialog(self, "Delete Contact",
                                f"Permanently delete '{name}'?")
        self.wait_window(dlg)
        if not dlg.result:
            return
        self._db.delete_contact(self._selected_id)
        self._selected_id = None
        self._refresh_all()
        self._toast("Contact deleted.", "info")

    def _on_toggle_fav(self, _event=None) -> None:
        if not self._selected_id:
            return
        try:
            is_fav = self._db.toggle_favorite(self._selected_id)
            self._refresh_all()
            state = "added to" if is_fav else "removed from"
            self._toast(f"Contact {state} favourites.", "success")
        except ValueError as exc:
            self._toast(str(exc), "error")

    def _on_search(self) -> None:
        query = self._search_var.get().strip()
        if not query:
            self._load_contacts()
            return
        results = self._db.search_contacts(query)
        self._load_contacts(results)

    def _clear_search(self) -> None:
        self._search_var.set("")
        self._search_entry.focus()

    def _switch_view(self, view: str) -> None:
        self._current_view = view
        c = self._colors
        titles = {"all": "All Contacts", "favorites": "★  Favourites"}
        self._view_title.configure(text=titles.get(view, "Contacts"))
        for key, btn in self._nav_buttons.items():
            btn.set_active(
                key == view,
                active_color=c["accent_dim"],
                inactive_color="transparent",
                text_active=c["text_primary"],
                text_inactive=c["text_secondary"],
            )
        self._clear_search()
        self._load_contacts()

    def _on_export(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export Contacts",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            count = self._db.export_to_csv(path)
            self._toast(f"Exported {count} contacts.", "success")
        except Exception as exc:
            self._toast(f"Export failed: {exc}", "error")

    def _on_import(self) -> None:
        path = filedialog.askopenfilename(
            title="Import Contacts from CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            imported, skipped = self._db.import_from_csv(path)
            self._refresh_all()
            self._toast(
                f"Imported {imported} contacts. {skipped} skipped.", "success"
            )
        except Exception as exc:
            self._toast(f"Import failed: {exc}", "error")

    def _show_context_menu(self, event) -> None:
        row = self._tree.identify_row(event.y)
        if row:
            self._tree.selection_set(row)
            self._on_tree_select()
            self._ctx_menu.tk_popup(event.x_root, event.y_root)

    # ── Sorting ───────────────────────────────────────────────────────────────

    _sort_reverse: dict[str, bool] = {}

    def _sort_tree(self, col: str) -> None:
        data = [
            (self._tree.set(k, col), k)
            for k in self._tree.get_children("")
        ]
        rev  = self._sort_reverse.get(col, False)
        data.sort(reverse=rev)
        for idx, (_, k) in enumerate(data):
            self._tree.move(k, "", idx)
        self._sort_reverse[col] = not rev

    # ══════════════════════════════════════════════════════════════════════════
    # Theme
    # ══════════════════════════════════════════════════════════════════════════

    def _toggle_theme(self) -> None:
        self._mode = "light" if self._mode == "dark" else "dark"
        ctk.set_appearance_mode(self._mode)
        self._colors = COLORS[self._mode]
        self._apply_ttk_style()
        self._load_contacts()

    def _apply_ttk_style(self) -> None:
        c   = self._colors
        stl = ttk.Style(self)
        stl.theme_use("clam")
        stl.configure(
            "ContactBook.Treeview",
            background=c["table_row_odd"],
            foreground=c["text_primary"],
            fieldbackground=c["table_row_odd"],
            rowheight=36,
            font=FONTS["table_body"],
            borderwidth=0,
        )
        stl.configure(
            "ContactBook.Treeview.Heading",
            background=c["table_header"],
            foreground="#FFFFFF",
            font=FONTS["table_header"],
            relief="flat",
            padding=(6, 6),
        )
        stl.map(
            "ContactBook.Treeview",
            background=[("selected", c["table_select"])],
            foreground=[("selected", c["text_primary"])],
        )

    # ══════════════════════════════════════════════════════════════════════════
    # Utilities
    # ══════════════════════════════════════════════════════════════════════════

    def _toast(self, message: str, kind: str = "info") -> None:
        ToastNotification(self, message, kind=kind)
