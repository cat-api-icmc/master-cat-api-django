# Deploy instructions:

This project is deployed using Docker and Docker Compose but it can also be run locally without Docker.

## Build and Run Locally without Docker

To build and run the project locally without Docker, follow these steps:

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the Django development server:
   ```bash
    python manage.py runserver
   ```
3. Make sure to set up your environment variables as needed, such as database configurations and secret keys
   (this step is also needed when using Docker).

## Build and Run Local with Docker

To build and run the local environment, use the following command:

```bash
docker compose build --no-cache && docker compose up -d
```

## Deploy to Production

To deploy the project to production, use the following command:

```bash
docker compose build --no-cache && docker push brunosilvestre00/django-cat-api
```
