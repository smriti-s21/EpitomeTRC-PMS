@echo off
echo Installing required packages for PMS...
python install_packages.py
echo.
echo Running database migrations...
python migrate_db.py
echo.
echo Setup complete! You can now run the application with:
echo python app.py
pause