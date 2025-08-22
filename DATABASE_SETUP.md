# Database Setup

## Quick Setup

1. **Start PostgreSQL service:**
   ```bash
   sudo systemctl start postgresql@16-main
   ```

2. **Set PostgreSQL password for user 'postgres':**
   ```bash
   sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
   ```

3. **Create database (if needed):**
   ```bash
   ./setup_db.sh
   ```

4. **Run Django migrations:**
   ```bash
   source venv/bin/activate
   python manage.py migrate
   ```

## Manual Database Creation

If you prefer to create the database manually:

```bash
sudo -u postgres psql -c "CREATE DATABASE testguru;"
```

## Troubleshooting

- **Authentication failed**: Make sure PostgreSQL password is set correctly
- **Database not found**: Run `./setup_db.sh` to create it automatically
- **Permission denied**: Make sure PostgreSQL service is running

## Note

Django migrations create tables but don't create the database itself. The `setup_db.sh` script automatically creates the `testguru` database if it doesn't exist.
