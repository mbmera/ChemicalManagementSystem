# Chemical Management System

A Streamlit application for managing a laboratory's chemical inventory and related safety records. The app uses a local SQLite database and keeps chemical registration, stock tracking, SDS management, and archive workflows in one interface.

## Features

- Register chemicals and search active inventory by product name, CAS number, or storage location.
- View and edit chemical details, units, and low-stock thresholds.
- Record received, used, and disposed stock, with balance and movement history.
- Upload, download, and remove SDS PDF versions; record review dates.
- View SDS review alerts, missing SDS records, and stock alerts on the dashboard.
- Archive chemicals and restore archived records.

## Requirements

- Python 3.8.3
- Dependencies listed in `requirements.txt` (Streamlit 1.40.1 and pandas 2.0.3).

## Setup

From the project directory, create and activate a virtual environment:

```powershell
py -3.8 -m venv .venv
.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run

Start the app from the project directory:

```powershell
streamlit run app.py
```

The application uses a local SQLite database. Database files and SDS/PDF files are excluded from Git; keep backups of any local records you need to retain.
