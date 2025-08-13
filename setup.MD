# Telemetry Sleuth Rocky Linux Setup Instructions

## 1. Update the System
```sh
sudo dnf update -y
```

## 2. Install Required Packages
```sh
sudo dnf groupinstall "Development Tools" -y
sudo dnf install gcc make python3 python3-pip git -y
```

## 3. (Optional) Install PostgreSQL
```sh
sudo dnf install postgresql-server postgresql-contrib -y
sudo postgresql-setup --initdb
sudo systemctl enable --now postgresql
```

## 4. Set Up PostgreSQL Database and User
```sh
sudo -i -u postgres
psql
-- In the psql prompt:
ALTER USER postgres WITH PASSWORD 'postgres123';
CREATE DATABASE telemetrysleuth;
\q
exit
```

## 5. Clone Your Repository
```sh
mkdir -p ~/code
cd ~/code
git clone https://github.com/aarondyck/telemetrysleuth.git
cd telemetrysleuth
```

## 6. Set Up Python Virtual Environment
```sh
python3 -m venv venv
source venv/bin/activate
```

## 7. Install Python Dependencies
```sh
pip install --upgrade pip
pip install -r requirements.txt
```

## 8. Configure Environment Variables
```sh
cp .env.example .env
nano .env
```
Set these values in `.env` for local testing:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=telemetrysleuth
DB_USER=postgres
DB_PASSWORD=postgres123
```
Adjust other settings as needed.


## 9. Run the Application
- **Web app:**
  ```sh
  python scripts/app.py
  ```
- **TCP listener (in a separate terminal if needed):**
  ```sh
  python scripts/tcp_listener.py
  ```

## 10. Access the Application
- Open your browser to [http://localhost:5000](http://localhost:5000) for the web interface.

---

**You are now running your application on a fresh Rocky Linux server!**
If you encounter errors, check the logs/output for details and ensure your `.env` matches your database setup.