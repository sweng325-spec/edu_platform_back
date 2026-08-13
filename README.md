python -m venv venv

venv\Scripts\activate


pip install --upgrade pip
pip install -r requirements.txt



# Run migrations
python manage.py makemigrations
python manage.py migrate


Step 1: Find Your Local IP Address
On Windows (CMD/PowerShell):

DOS
ipconfig
(Look for IPv4 Address under your active Wi-Fi or Ethernet adapter, e.g., 192.168.1.15)


python manage.py runserver 0.0.0.0:8000