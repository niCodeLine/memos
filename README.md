# memos

FastAPI - PostgreSQL - Redis implementation to track your memos.

A robust and lightweight RESTful API to manage your personal reminders, 
tasks, and memos.
This project offers different versions for various needs and scalability 
requirements.

## Available Versions 📦

### 📦 Basic Version (`main` branch)
**FastAPI - PostgreSQL - Redis implementation**
- Core RESTful API for memo management
- Full CRUD operations for reminders
- Strict Date Validation preventing assigning non-existent days to months.
- PostgreSQL & Redis database integration
- Flexible Network Exposure with instructions to run locally or across your home
network (LAN).

### 🚀 Enhanced Version (`feature/google-assistant-integration` branch)  
**FastAPI - PostgreSQL - Redis - Google ADK implementation**
- All Basic Version features +
- Google Assistant integration with NLP for memo management
- Bots integration capability


## 1. Prerequisites 📦
Before starting, ensure you have:
- **Python 3.10+**
- **Redis**
- **PostgreSQL** installed and running (shown how to set up one below)
---


## 2. Installation & Setup ⚙️
Clone this repository and move into its folder.
If preferred, a virtual environment can be created by running `python -m venv venv` in the repository folder.
If that's the case, make sure to have it activated to proceed.

### Step 2.1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2.3: Configure Environment Variables 🔐
The application reads configuration from `.env`.
Create it from the `.env.example` template and edit it to your preferred `name` and `password`. It can also be left untouched.
```python
POSTGRES_HOST=localhost
POSTGRES_DB=reminders
POSTGRES_USER=user # <- your name
POSTGRES_PASSWORD=password # <- your password
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```
*Avoid changing the other variables.*

Rename the file to `.env`, or create it with:
```bash
cp .env.example .env
```

---
## 3. Database Setup (Crucial Step) 🗄️
Before booting up the API server, the database must be created.

### Step 3.1: Running and Creating the Database
When postgresql and redis are installed, start the services:

#### macOS
Initialize Redis:
```bash
brew services start redis
```
Stop Redis:
```bash
brew services stop redis
```

Initialize PostgreSQL:
```bash
brew services start postgresql
psql postgres
```
Stop PostgreSQL:
```bash
brew services stop postgresql
```

#### Linux
Initialize Redis:
```bash
sudo systemctl start redis
sudo systemctl enable redis
```
Stop Redis:
```bash
sudo systemctl stop redis
```

Initialize PostgreSQL:
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres psql
```
Stop PostgreSQL:
```bash
sudo systemctl stop postgresql
```

#### Windows
Initialize Redis:
```bash
redis-server
```
Stop Redis:
```bash
# Use Task Manager or redis-cli shutdown command
```

Initialize PostgreSQL:
```bash
net start postgresql
psql -U postgres
```
Stop PostgreSQL:
```bash
net stop postgresql
```

*Note: Redis can also be started with the command `redis-server` on all 
platforms if preferred.*


* Note: The database must be running for the API to work. Ensure it is not in use before stopping it.

Once you are in the PostgreSQL CLI, create a user and password **matching the ones set in the `.env` file**.

```sql
-- 1. Create the application user matching your environment setup
CREATE USER user WITH PASSWORD 'password';

-- 2. Create the database owned by this user
CREATE DATABASE reminders OWNER user;

-- 3. Grant privileges to the user
GRANT ALL PRIVILEGES ON DATABASE reminders TO user;
```
---


## 4. Running the API ▶️
For improved reliability, always start Uvicorn from the directory containing the
`api/` folder.

*(Note: Ensure PostgreSQL is running and the credentials match your
environment settings).*

### Mode A: Local Development
API is only accessible from your own computer.
```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
### Mode B: Home Network Access
API is accessible to any device connected to the **same Wi-Fi network**.
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```
To access from another device, find your local IP address and navigate to it
adding `:8000` at the end (e.g., `192.168.1.45` -> `http://192.168.1.45:8000`).
---


## 6. API Endpoints Reference
Once running, explore the interactive documentation natively generated at `/docs`.
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

### Example Request
```bash
curl -X POST "http://127.0.0.1:8000/reminders" \
-H "Content-Type: application/json" \
-d '{"day": 14, "month": 4, "text": "Juanito's birthday"}'
```