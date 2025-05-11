# Backend for project
## Requires
- Python 3.11.x (Необхідно для майбутнього використання tensorflow. Я писав на Python 3.11.9)
## Setup
**Windows**:
```
python3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Для роботи з базою даних, потрібно встановити PostgreSQL, створити і заповнити `.env` файл в папці `scrapper`.<br>

Приклад `.env`:
```
DB_HOST="localhost"
DB_NAME="database_name"
DB_USER="your_username"
DB_PASSWORD="your_password"
DB_PORT="your_port"
```