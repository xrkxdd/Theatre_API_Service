Theatre_API_Service

Before you can run this project, make sure you have the following installed:

Python 3.8 or higher
Django 3.2 or higher
pip
Docker


## Running the API with Python
git clone https://github.com/xrkxdd/Theatre_API_Service.git
cd Theatre_API_Service
python3 -m venv venv
source venv/bin/activate (on macOS)
venv\Scripts\activate (on Windows)
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver


## Running the API with Docker

git clone https://github.com/xrkxdd/Theatre_API_Service.git
cd Theatre_API_Service

create an .env file in the root directory of project:
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=db
    DB_PORT=5432
    SECRET_KEY=your_secret_key

docker-compose build
docker-compose up
