# Threadly

A simple, lightweight e-commerce website for a custom-made T-shirt business.
"Made by you. Worn by you."

## Technologies Used

* HTML5 / CSS3 (Vanilla, Responsive)
* JavaScript (Vanilla)
* Python 3
* Django
* SQLite (Development Database)

## Installation Instructions

1. Clone the repository or download the source code.
2. Ensure you have Python 3 installed.
3. Open a terminal and navigate to the project directory.

## Virtual Environment Setup

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Database Migrations

Run the following commands to create the database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Creating a Superuser

To access the Django Admin panel, you need a superuser account:

```bash
python manage.py createsuperuser
```
Follow the prompts to set a username, email, and password.

## Running the Development Server

Start the local server with:

```bash
python manage.py runserver
```

Then open your browser and go to `http://127.0.0.1:8000/`.

## How to Add Products

1. Log in to the admin panel at `http://127.0.0.1:8000/admin/`.
2. Click on **Products** under the **Store** section.
3. Click **Add Product** in the top right.
4. Fill in the details (name, description, price, category, etc.).
5. Provide available colors and sizes as comma-separated values (e.g., `S, M, L` and `Black, White`).
6. Upload an image (optional but recommended).
7. Save the product.

## Basic Deployment Instructions

To deploy this application to a basic hosting platform (like Heroku, Render, or PythonAnywhere):

1. Set up a PostgreSQL or MySQL database on your host and update the `DATABASES` configuration in `settings.py`.
2. Set the `SECRET_KEY` environment variable on your host. Do not hardcode it in production.
3. Set `DEBUG = False` in `settings.py` via environment variable.
4. Update `ALLOWED_HOSTS` in `settings.py` to include your production domain.
5. Configure static file serving (e.g., using `whitenoise`).
6. Run `python manage.py collectstatic`.
7. Use a production WSGI server like `gunicorn` to run the application (e.g., `gunicorn threadly.wsgi`).
