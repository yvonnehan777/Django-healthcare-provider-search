# 🏥 Django Healthcare Provider Search
A web-based application built with **Django** and **PostgreSQL**, designed for efficient searching, filtering, and management of healthcare provider records. This project demonstrates scalable backend design, clean code structure, and an interactive, responsive front-end UI.

## Features
- **Advanced Search** — Filter providers by name, taxonomy, state, address, and specialty.
- **Pagination** — Smooth navigation across large datasets  
- **PostgreSQL Integration** — Structured and normalized database schema  
- **Responsive UI** — Adapts seamlessly to desktop and mobile layouts  
- **Modular Architecture** — Easy to maintain, extend, and deploy  

## 🧩 Project Structure
Django-healthcare-provider-search/
│
├── healthcare_search/                 → Main project configuration (settings, urls, wsgi)
│
├── medicaid_providers_lookup/         → Core app handling search and filtering
│   ├── models.py                      → Defines provider and taxonomy models
│   ├── views.py                       → Search logic and query handling
│   ├── urls.py                        → URL routing for search endpoints
│   └── templates/search.html          → HTML template for the search interface
│
├── scripts/                           → Utility scripts for data loading
│   └── import_data.py
│
├── static/                            → Static assets (CSS, JS, images)
├── manage.py                          → Django management entry point
└── requirements.txt                   → Python dependencies

## ⚙️ Installation Guide
1️⃣ Clone the repository
git clone https://github.com/yvonnehan777/Django-healthcare-provider-search.git
cd Django-healthcare-provider-search

2️⃣ Create a virtual environment
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Configure the database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'provider_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

5️⃣ Run migrations
python manage.py migrate

6️⃣ Start the development server
python manage.py runserver

Then visit http://127.0.0.1:8000/ in your browser 🚀
