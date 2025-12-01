**Catering Event Management System**

A Django-based event & workforce management system designed for catering staff and catering boys, featuring event scheduling, seat allocation, profile management, and Razorpay-powered payments.

** Overview**

This project streamlines the workflow of catering event management.
It provides two user roles:

Staff – manages events, boys, registrations, and payments

Catering Boys – register for events, view payments, update profiles

The system includes dashboards, role-based authentication, image uploads, and a clean Bootstrap UI.

  **Key Features**

** Staff Module**

Add, edit, and manage catering boys

Create, update, delete events

Upload event images

Track registrations & available seats

Mark events as completed

Manage payment history

Make payments via Razorpay

Simulate payments (dev mode)

Staff dashboard with analytics:

Total boys

Total events

Upcoming events

Pending payments

   **Catering Boy Module**

Login + first-time password setup

View & filter events (search, sort, pagination)

Register for events (auto seat assignment)

Profile update:

Profile picture

Mobile number

Email

UPI ID

View registration history

View payment history

Boy dashboard

 **UI / System Features**

Responsive Bootstrap 5 interface

Dark/Light mode toggle (saved in localStorage)

Default placeholders for profile & event images

Media uploads for images

Clean Django Class-Based Views

Custom User Model (Staff + Boy roles)

 **Tech Stack**

Backend: Django, Python

Frontend: HTML, Bootstrap 5, JavaScript

Database: SQLite / MySQL

Payments: Razorpay API

Authentication: CustomUser (extends AbstractUser)

Media: Django File Uploads

 **Setup & Installation**
1️⃣ Clone repository
git clone https://github.com/ameen-git9/catering-event-management-system.git
cd catering-event-management-system

2️⃣ Create virtual environment
python -m venv env
env\Scripts\activate     # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Configure Razorpay

Add in settings.py:

RAZORPAY_KEY_ID = "your_key_id"
RAZORPAY_KEY_SECRET = "your_key_secret"

5️⃣ Apply migrations
python manage.py migrate

6️⃣ Create superuser
python manage.py createsuperuser

7️⃣ Start development server
python manage.py runserver
