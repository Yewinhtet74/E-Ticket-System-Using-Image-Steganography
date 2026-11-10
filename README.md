# Enhance Security of Airline E-Ticket System Using Image Steganography

B.E. thesis project: **YE Air International**, a Flask web app that lets passengers search flights, book a seat and download an e-ticket. They then use that e-ticket to find their check-in counter and to check in on their own. Airport staff use the admin pages to open check-in counters and track which passengers have checked in.

Each e-ticket carries hidden, encrypted data, so the system can tell an original ticket from a fake or edited one:

1. A random secret code is encrypted with **AES-128 (CBC)** using a key and IV made just for that ticket.
2. The encrypted code and the ticket number are hidden in the **least significant bits** of the ticket's logo (steganography).
3. When a ticket is uploaded, the app reads those bits back and decrypts them with that ticket's key. It accepts the ticket only if the secret code is in the database.

---

## Requirements

| Software | Version | Notes |
|---|---|---|
| Windows | 10 / 11 | The ticket text uses the Arial font, which comes with Windows |
| Python | 3.10 | Python 3.9 also works |
| MySQL Server | 8.0 | User `root`, password `root` (see [Database settings](#database-settings)) |
| Internet | (first run only) | Needed to download the Python packages |

---

## Quick start (one click)

1. **Install MySQL Server 8.0** if it isn't installed.
   - Open **MySQL Installer**, click **Add**, choose **MySQL Server 8.0**, then **Execute**.
   - When the installer asks for the root password, use **`root`**.
   - Leave the port at **3306** and keep "Start the MySQL Server at System Startup" ticked.
2. **Double-click `run_project.bat`** in this folder. It will:
   1. Create a `venv` folder with Python 3.10 and install the packages in `requirements.txt` (first run only; takes a few minutes).
   2. Check MySQL, and create `airline_database` from `setup_database.sql` if it doesn't exist. **An existing database is never changed.**
   3. Start the website and open **http://127.0.0.1:5000** in your browser.
3. To stop the server, press **Ctrl + C** in the black window, or close it.

---

## Manual setup (step by step)

Run these in **Command Prompt**:

```bat
:: go to the project folder (change the path to where you saved it)
cd /d "C:\path\to\project"

:: 1. Create a virtual environment with Python 3.10
py -3.10 -m venv venv
:: (if "py" is not recognized, use the full path instead:)
:: "C:\Program Files\Python310\python.exe" -m venv venv

:: 2. Activate it and install the packages
venv\Scripts\activate
pip install -r requirements.txt

:: 3. Create the database (only if it doesn't exist yet)
python check_setup.py

:: 4. Run the app
python app.py
```

Then open **http://127.0.0.1:5000**.

> **PowerShell users:** activate with `venv\Scripts\Activate.ps1`. If scripts are blocked, run
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or just use Command Prompt.

### Other ways to create the database

- **MySQL Workbench:** connect as `root`, choose **File > Open SQL Script**, select `setup_database.sql`, then click the ⚡ (Execute) button.
- **mysql command line:**
  ```bat
  "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < setup_database.sql
  ```

### Debug mode (auto-reload when you edit code)

```bat
venv\Scripts\activate
set FLASK_ENV=development
flask run
```

---

## Using the app

### Passenger pages

| Page | URL | What it does |
|---|---|---|
| Home | `/` | Landing page |
| Search Flight | `/findflight` | Pick From, To, a date (tomorrow up to 2 months ahead) and a class, then book a seat and **download the e-ticket (PNG)** |
| Find Counter | `/findcounter` | Upload your e-ticket to see your check-in counter number and estimated opening time (2 hours before departure) |
| Check In | `/checkin` | Upload your e-ticket and enter the **counter passcode** given by the staff to check in |
| Notice / About | `/notice`, `/about` | Information pages |

> Always upload the **original downloaded PNG**. Screenshots and re-saved or compressed copies lose the hidden data and are rejected as invalid.

### Admin (staff) pages

Go to **http://127.0.0.1:5000/admin** and log in with:

| Username | Password |
|---|---|
| `admin` | `admin123` |

| Page | URL | What it does |
|---|---|---|
| Counter | `/admin/counter` | Choose a flight, date and counter number, then **open the counter**. This creates an 8-character passcode for passengers. **Close Counter** removes it |
| Dashboard | `/admin/dashboard` | For a flight and date, lists the passengers who **have** and **haven't** checked in |

### Typical walkthrough

1. Search **Yangon (RGN) to Bangkok (BKK)** for any date, book an Economy seat, and download the ticket.
2. Log in as admin and open a counter for that flight and date (for example, counter 3). Note the passcode.
3. Go to **Find Counter** and upload the ticket. It shows counter 3.
4. Go to **Check In**, upload the ticket and enter the passcode. You should see "checked in successfully".
5. Open the admin **Dashboard** for that flight and date. The passenger is now in the checked-in list.

---

## Sample flight data

`setup_database.sql` adds **54 sample flights**. They all fly between **Yangon (RGN)** and one other city. Flight numbers ending in an odd number fly from Yangon; even numbers fly back to Yangon. A flight runs only on its listed weekdays, so a search for another day finds **0 flights**.

| Route | Flight numbers | Days | From RGN (dep → arr, local time) | To RGN (dep → arr, local time) |
|---|---|---|---|---|
| RGN ⇄ Bangkok (BKK) | YE0101–YE0114 | Every day | 08:00 → 09:45 | 11:00 → 11:50 |
| RGN ⇄ Singapore (SIN) | YE0201–YE0208 | Mon, Wed, Fri, Sun | 10:30 → 14:50 | 16:00 → 17:30 |
| RGN ⇄ Kuala Lumpur (KUL) | YE0301–YE0306 | Tue, Thu, Sat | 09:15 → 13:15 | 14:30 → 15:35 |
| RGN ⇄ Ho Chi Minh (SGN) | YE0401–YE0406 | Mon, Thu, Sat | 13:00 → 15:40 | 17:00 → 18:45 |
| RGN ⇄ Jakarta (CGK) | YE0501–YE0504 | Tue, Fri | 07:30 → 12:00 | 13:30 → 17:10 |
| RGN ⇄ Manila (MNL) | YE0601–YE0604 | Wed, Sat | 11:00 → 16:20 | 17:30 → 20:00 |
| RGN ⇄ Seoul (ICN) | YE0701–YE0706 | Tue, Fri, Sun | 23:30 → 07:30 (+1 day) | 18:00 → 22:00 |
| RGN ⇄ Tokyo (HND) | YE0801–YE0806 | Mon, Thu, Sat | 22:00 → 07:00 (+1 day) | 11:00 → 16:15 |

Ticket prices for each class come from `price_of_route.json`. Airport and city names come from `city_code.json`.

---

## Database settings

The connection settings are in **`app.py`, lines 20–23**:

```python
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'airline_database'
```

If your MySQL password is different, change it here **and** at the top of `check_setup.py`.

### Tables in `airline_database`

| Table | Purpose |
|---|---|
| `plane` | Plane number and seat count for each class (first / business / premium / economy) |
| `route` | Flight number, from/to airport, weekday (1 = Mon … 7 = Sun), departure, arrival and flight times, plane number |
| `ticket` | Booked tickets: passenger, passport, flight, class, date, contact details, check-in time |
| `aes2` | AES key and IV for each ticket (used to verify uploaded tickets) |
| `aes` | One default key/IV row the code expects to exist |
| `checkincounter` | Open counters: flight, date, counter number, passcode |
| `adminaccount` | Admin usernames and passwords |

---

## Project structure

```
4.Project/
├── app.py               # Flask app: all routes and pages
├── mycollection.py      # Database queries: flights, prices, counters, check-in, admin login
├── ticket_center.py     # E-ticket creation (AES + steganography) and verification
├── ticket_writing.py    # Writes passenger and flight details onto the ticket image
├── city_code.json       # Airport codes → airport, city, country
├── price_of_route.json  # Ticket prices by destination, plane and class
├── templates/           # HTML pages (Jinja2)
├── static/images/       # Website images
├── images/              # Ticket template (sample ticket.png) and logo used on tickets
├── requirements.txt     # Python packages
├── setup_database.sql   # Creates airline_database with sample data
├── check_setup.py       # Checks MySQL; creates the database if it's missing
└── run_project.bat      # One-click setup and run (Windows)
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Cannot connect to MySQL on localhost:3306` | MySQL isn't running. Open **Services** (`services.msc`), find **MySQL80** and click **Start**. If it isn't listed, install MySQL Server (see Quick start). |
| `MySQL rejected user 'root' with password 'root'` | Your root password is different. Change it in `app.py` and `check_setup.py`, or reset it to `root`. |
| `'py' is not recognized` | Use the full path: `"C:\Program Files\Python310\python.exe" -m venv venv` |
| Package install failed on the first run | Check your internet connection and run `run_project.bat` again. It carries on from where it stopped. |
| Search shows **0 flights** | That route doesn't fly on that weekday. Check [Sample flight data](#sample-flight-data). |
| Uploaded ticket says **Invalid ticket** | Upload the original PNG you downloaded from the site. Tickets from a database that was deleted and rebuilt won't verify either. |
| `OSError: cannot open resource` when downloading a ticket | The Arial font wasn't found (non-Windows systems). Copy an `arial.ttf` file into the project folder. |
| Port 5000 is already in use | Close the other program, or run `flask run -p 5001` and open http://127.0.0.1:5001 |
| Want a fresh database | In MySQL Workbench run `DROP DATABASE airline_database;`, then run `python check_setup.py` again. **This deletes all booked tickets.** |
| Old `.venv` folder | It was built with Python 3.9, which is no longer installed, so it doesn't work. It's safe to delete; the project now uses `venv`. In PyCharm, set the interpreter to `venv\Scripts\python.exe`. |

---

## Note

This project is meant to run on your own computer for demonstration. The admin password is stored as plain text and the Flask secret key is written in the code, so don't put it on the public internet as it is.
