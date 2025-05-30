# onlineCAL

An online portal developed in Django to manage CAL BPHC's instrument booking process.

## Development Setup

### Prerequisites

- `git`
- `python` >= 3.10
- `poetry` >= 2.1.1
- `docker-compose` or `MySQL`

### Installation

1. Clone the repository

   ```bash
   git clone https://github.com/CAL-BPHC/onlineCAL.git
   ```

2. Install dependencies

   ```bash
   cd onlineCAL
   poetry sync --no-root
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
   python manage.py migrate
   ```

6. Create a superuser for accessing the admin panel

   ```bash
   python manage.py createsuperuser
   ```

7. Run the server

   ```bash
   python manage.py runserver
   ```

## Deployment

The deployment process is automated through GitHub Actions, with a [workflow](.github/workflows/deploy.yml) that triggers on every push to the `master` branch.

If, for any reason, changes need to be deployed manually, the following steps can be followed, as they mirror the actions performed by the workflow:

1. SSH into the server using the private key file provided
2. Navigate to the project directory

   ```bash
   cd /home/ubuntu/onlineCAL/server
   ```

3. Pull the latest changes from the repository

   ```bash
   git pull origin master
   ```

4. (Optional) Update dependencies if there have been any changes to them

   ```bash
   poetry sync --no-root
   ```

5. (Optional) Run migrations if there are any new ones

   ```bash
   python manage.py migrate
   ```

6. (Optional) Collect static files if there have been any changes

   ```bash
   python manage.py collectstatic
   ```

7. Restart supervisor

   ```bash
   sudo supervisorctl restart onlineCAL
   ```

## Hosting

Server configuration details are available [here](https://drive.google.com/drive/folders/1E3XOwm7TdjcMoLt7LjvtM0ODzSZpveAT?usp=sharing).
