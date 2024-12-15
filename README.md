# backend
Backend services for KhoshTrip

## Getting Started
First apply the migrations by running this command:
```commandline
python .\manage.py migrate 
```
To run the server locally you need to run this command:
```commandline
python .\manage.py runserver 
```

To access the database, first you should create a superuser:
```commandline
python .\manage.py createsuperuser
```
You should enter a username, an email address and a password.

After creating the user, you can login to the admin panel by adding `/admin` at the end of the url of the local server and enter the username and password.
