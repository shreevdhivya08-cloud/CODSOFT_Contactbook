# ◉ ContactBook

> A modern, production-ready desktop contact manager built with Python and CustomTkinter.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2%2B-purple?style=flat-square)
![SQLite](https://img.shields.io/badge/Storage-SQLite-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

##  Features

### Contact Management
- **Add / Edit / Delete** contacts with a clean modal form
- **Search** across name, phone number, and email in real time
- **Favourite** contacts with one click — accessible via dedicated sidebar view
- **Sortable table** — click any column header to sort ascending/descending
- **Double-click** a row or right-click for a context menu (Edit / Favourite / Delete)

### Rich Contact Fields
| Field | Description |
|-------|-------------|
| Full Name | Required |
| Phone Number | Required · must be unique |
| Email Address | Optional · validated format |
| Address | Optional free text |
| Company | Optional |
| Notes | Optional multi-line |

### Dashboard
Four live stat cards update whenever data changes:
- **Total** contacts
- **Favourites** count
- **With Email** count
- **Companies** count

### Data Storage
- **SQLite** — zero-config, single-file database (`database/contacts.db`)
- Created automatically on first run — no setup required
- All data persists between sessions

### Import / Export
- **Export to CSV** — saves all contacts to a file you choose
- **Import from CSV** — ingests contacts, skipping duplicates gracefully

### UI / UX
- **CustomTkinter** with a deep-indigo / vivid-violet colour palette
- **Dark / Light mode toggle** (sidebar bottom)
- Sidebar navigation with active-state highlighting
- Toast notifications for all actions
- Confirmation dialog before destructive deletes
- Detail panel with avatar initials, all contact fields, and quick-action buttons

### Validation
- Duplicate phone number prevention
- Email format validation (regex)
- Required-field checks with inline error messages

---

##  Installation

### Prerequisites
- Python 3.11 or later
- `tkinter` (usually bundled; on Ubuntu: `sudo apt install python3-tk`)

### Steps

```bash
# 1. Clone / download this repository
git clone https://github.com/you/contactbook.git
cd contactbook

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python main.py
```

---

##  Project Structure

```
contactbook/
├── main.py                 # Entry point
├── requirements.txt
├── README.md
├── database/
│   ├── __init__.py
│   ├── db_manager.py       # All SQLite CRUD + validation
│   └── contacts.db         # Auto-created on first run
└── ui/
    ├── __init__.py
    ├── app.py              # Main application window
    ├── contact_form.py     # Add / edit modal dialog
    ├── theme.py            # Colour palette, fonts, spacing
    └── widgets.py          # Reusable widget components
```

---

##  Architecture

| Layer | Module | Responsibility |
|-------|--------|----------------|
| Data  | `database/db_manager.py` | SQLite CRUD, validation, CSV I/O |
| View  | `ui/app.py` | Main window, layout, event wiring |
| Form  | `ui/contact_form.py` | Add/edit modal |
| Theme | `ui/theme.py` | All design tokens |
| Widgets | `ui/widgets.py` | Reusable components |

---

##  Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Delete` | Delete selected contact |
| `Double-click` | Edit selected contact |
| Right-click | Context menu |

---

##  CSV Format

Exported / imported files use these column headers (order matters for import):

```
full_name,phone,email,address,company,notes,favorite
```

`favorite` is `1` for starred contacts and `0` otherwise.

---

## License

MIT — free to use, modify, and distribute.
