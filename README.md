# Airport-API-Service

A Django REST API service for managing airport operations, including airplanes, flights, routes, and ticket booking.

## Features

- User authentication and authorization
- Comprehensive API documentation (available at `/api/v1/doc/swagger/`)
- Integrated Django admin panel for managing models and data
- Airplane and airplane type management
- Airport and route management
- Flight scheduling
- Ticket booking system
- Order management
- Image handling for airplanes
- RESTful API endpoints
- Filtering capabilities for flights, routes, and airplanes

## Tech Stack

- Python 3.11
- Django
- Django REST Framework
- PostgreSQL
- Gunicorn
- Docker
- Docker-Compose

## Installation and Setup

1. Clone the repository:

```bash
git clone https://github.com/zave52/Airport-API-Service.git
cd Airport-API-Service
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL credentials:

   Ensure that you have PostgreSQL installed and configure the following environment variables with your database
   credentials:

   ```bash
   export DB_NAME=<your_database_name>
   export DB_USER=<your_database_user>
   export DB_PASSWORD=<your_database_password>
   export DB_HOST=<your_database_host>
   export DB_PORT=<your_database_port>
   ```

5. Set up Django secret key:

   Add the following environment variable for the Django project secret key:

   ```bash
   export SECRET_KEY=<your_secret_key>
   ```

6. Apply migrations:

```bash
python manage.py migrate
```

7. Collect static files:

```bash
python manage.py collectstatic
```

8. Create superuser (admin):

```bash
python manage.py createsuperuser
```

9. Run the development server:

```bash
python manage.py runserver
```

10. Access the application at: http://127.0.0.1:8000/

## Getting Access

To access the API, users need to:

1. **Register:** Send a POST request to the `/api/v1/user/register/` endpoint with their details to create an account.
2. **Get Token:** After registering, send a POST request to the `/api/v1/user/token/` endpoint with their login
   credentials to
   receive an access token.
3. **Use Token:** Include the received token in the `Authorization` header for each API request:

   ```http
   Authorization: Bearer <your_token>
   ```

## Running with Docker-Compose

1. Ensure you have Docker and Docker-Compose installed on your system.

2. Clone the repository (if not already done):

```bash
git clone https://github.com/zave52/Airport-API-Service.git
cd Airport-API-Service
```

3. Set up environment variables:

   Create a `.env` file in the root directory and provide the following:

   ```env
   DB_NAME=<your_database_name>
   DB_USER=<your_database_user>
   DB_PASSWORD=<your_database_password>
   DB_HOST=db
   DB_PORT=5432
   SECRET_KEY=<your_secret_key>
   ```

4. Build and run the containers:

```bash
docker-compose up --build
```

5. The server will be running at `http://0.0.0.0:8000`.
