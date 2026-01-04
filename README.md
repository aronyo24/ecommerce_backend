# Ecommerce Backend

This is the backend for the Ecommerce application, built with Django and Django Rest Framework.

## Prerequisites

- Docker
- Docker Compose

## Running with Docker

1.  Navigate to the `docker` directory:

    ```bash
    cd docker
    ```

2.  Build and start the containers:

    ```bash
    docker compose up -d --build
    ```

    *Note: If you are using an older version of Docker Compose, you might need to use `docker-compose` instead of `docker compose`.*

3.  The application will be available at `http://localhost:8000`.

## Managing the Application

### Create a Superuser

To access the Django Admin interface, you need to create a superuser.

```bash
docker exec -it ecommerce_backend python manage.py createsuperuser
```

### Seed the Database

To populate the database with initial data (categories, products) and a default admin user:

```bash
docker exec -it ecommerce_backend python manage.py seed_data
```

This will create:
- Admin user: `admin` / `admin123`
- Categories: Electronics, Clothing
- Products: iPhone 15, MacBook Pro, T-Shirt

### View Logs

To see the logs of the backend service:

```bash
docker logs -f ecommerce_backend
```

### Stop Containers

To stop the running containers:

```bash
docker compose down
```

## Project Structure

- `apps/`: Contains the Django apps (authentication, core, orders, payments, products).
- `config/`: Project configuration settings.
- `docker/`: Docker configuration files.
- `requirements.txt`: Python dependencies.
