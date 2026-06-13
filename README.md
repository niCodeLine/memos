# memos
FastAPI - postgreSQL implementation to keep your memo's save.

A robust and lightweight RESTful API built with **FastAPI** and **PostgreSQL** to
manage your personal reminders, tasks, and memos.

## Features
- **Full CRUD operations** for managing reminders.
- **Strict Date Validation**: Prevents assigning non-existent days to specific
months (e.g., February 30th or September 31st).
- **Environment Driven**: Fully configurable via environment variables
(`os.getenv`).
- **Flexible Network Exposure**: Instructions to run locally, across your home
network (LAN), or globally (WAN).
---



## 1. Prerequisites
Before getting started, ensure you have the following installed on your local
machine:
- **Python 3.10** or higher.
- **PostgreSQL Database Server** (shown how to build one in Steps 3).
---


## 2. Installation & Environment Setup
Clone or download de project and navigate to the folder.
If prefered, a virtual environment can be created via `python -m venv venv` in its propper folder.
If that's the case, make sure to have it activated to proceed.

### Step 2.1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2.3: Configure Environment Variables
The application looks for environment variables to connect to PostgreSQL.
They have to be set by editing the .env.example file to your prefered `name` and `password`. It can also stay untouched.
```
POSTGRES_HOST=localhost
POSTGRES_DB=reminders
POSTGRES_USER=user # <- your name
POSTGRES_PASSWORD=password # <- your password
POSTGRES_PORT=5432
```
*Avoid changing the other variables.*

Change the file name to `.env`, or create it with:
```bash
cp .env.example .env
```

---
## 3. Database Initialization (Crucial Step)
Before booting up the API server, the database must be created.

### Step 3.1: Running and Createing the Database
When postgresql is installed continue with ur OS:
#### macOS
Inizialize:
```bash
brew services start postgresql
```
Enter:
```bash
psql postgres
```
Stop:
```bash
brew services stop postgresql
```
#### Linux
Inizialize:
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```
Enter:
```bash
sudo -u postgres psql
```
Stop:
```bash
sudo systemctl stop postgresql
```
#### Windows
```bash
net start postgresql
```
Enter:
```bash
psql -U postgres
```
Stop:
```bash
net stop postgresql
```
* Note: The database must be running for the API to work. Make sure the database is no longer being used before stoping it.

Once you are in, create USER and PASSWORD **matching the ones set before at the .env file**.
```sql
-- 1. Create the application user matching your environment setup
CREATE USER user PASSWORD 'password';
-- 2. Create the target database owned by this user
CREATE DATABASE reminders OWNER test;
-- 3. Grant administrative schema rights
GRANT ALL PRIVILEGES ON DATABASE reminders TO user;
```
---


## 4. Running the Application
For importing reliability, always trigger Uvicorn from the directory containing the
`api/` folder.

*(Note: Ensure your database server is running and the credentials match your
environment settings).*

### Mode A: Local Development
API only accessible from your own computer.
```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
### Mode B: Home Network Access
API accessible to any device connected to the **same Wi-Fi network**.
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

*To access from your phone, find your PC's local IP address (e.g., `192.168.1.45`
via `ipconfig` or `ip a`) and navigate to `http://192.168.1.45:8000/docs` in your
phone's browser.*
---


## 6. API Endpoints Reference
Once running, explore the interactive documentation natively generated at `http://
127.0.0.1:8000/docs`.
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/` | Base health check. Verifies the server is operational. |
| **POST** | `/reminders` | Creates a new reminder after verifying date
constraints. |
| **GET** | `/reminders` | Fetches reminders. Supports optional query filters
(`day`, `month`, `text`). |
| **GET** | `/reminders/{id}` | Retrieves a single detailed reminder matching the
given ID. |
| **DELETE**| `/reminders/{id}` | Deletes the specified reminder and returns the
deleted record payload. |

### Quick Test Example (Using `curl`)
curl -X POST "[http://127.0.0.1:8000/reminders](http://127.0.0.1:8000/reminders)" \
     -H "Content-Type: application/json" \
     -d '{"day": 13, "month": 6, "text": "Deploy project to production server"}'