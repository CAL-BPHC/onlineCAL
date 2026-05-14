# onlineCAL

An online portal developed in Django to manage CAL BPHC's instrument booking process.

## Development Setup

### Prerequisites

- `git`
- `python` >= 3.10
- `uv`
- `docker-compose` or `MySQL`

### Installation

1. Clone the repository

   ```bash
   git clone https://github.com/CAL-BPHC/onlineCAL.git
   ```

2. Install dependencies

   ```bash
   cd onlineCAL
   uv sync
   ```

3. Setup the database

   - The project uses MySQL as the database. You can either install MySQL or use the [docker-compose file](server/docker-compose.yaml) provided.

   - If you are using MySQL, create a database that you will use for the project.

   - If you are using the docker-compose file, run the following command

     ```bash
     docker-compose -f server/docker-compose.yaml up
     ```

   - Create a `db.conf` file in the `server` directory following the format in [`db.conf.example`](server/db.conf.example). Use the same details if you're using Docker; otherwise, adjust them to match your MySQL setup.

4. Change directory

   ```bash
   cd server
   ```

5. Run the migrations

   ```bash
   uv run python manage.py migrate
   ```

6. Create a superuser for accessing the admin panel

   ```bash
   uv run python manage.py createsuperuser
   ```

7. Run the server

   ```bash
   uv run python manage.py runserver
   ```

## Deployment

The deployment process is completely automated through GitHub Actions. The [deploy workflow](.github/workflows/deploy.yml) triggers automatically on every push to the `master` branch, and can also be triggered manually from the "Actions" tab on GitHub.

## Hosting

Server configuration details are available [here](https://drive.google.com/drive/folders/1E3XOwm7TdjcMoLt7LjvtM0ODzSZpveAT?usp=sharing).
