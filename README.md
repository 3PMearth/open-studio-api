# 3PM Open Studio API


## Installation
1. To install the required packages, run the following command in the project directory:
```
pip install -r requirements.txt
```
2. Create .env file from .env.sample and fill in the required fields:
```
cp .env.sample .env
```
3. And then run the following command to create the database:
```
python manage.py migrate
```
4. Create a superuser:
```
python manage.py createsuperuser
```
5. Run Celery:
```
celery --app=studio_api worker --loglevel=INFO
```
6. Run the server:
```
python manage.py runserver
```
7. Open the browser and go to the following address to see the API documentation:
```
http://127.0.0.1:8000/api-doc
```

## Requirements
- Python 3.9.7
- Django 4.2.3
- djangorestframework 3.14.0
- django-cors-headers 4.2.0
- and other packages in requirements.txt

## Database
- PostgreSQL 13.4

## API Documentation
- [Swagger](https://127.0.0.1:8000/api-doc)

## Usage
```
python manage.py runserver
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT License

## Authors
3PM Inc. (https://3pm.earth)




