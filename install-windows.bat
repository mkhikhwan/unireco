@echo off
echo Beginning installation...

python -m venv venv
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate

echo Installation complete. Please run runserver.bat to launch server.
pause
