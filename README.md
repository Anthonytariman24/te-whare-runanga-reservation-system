Django Hotel Reservation - Minimal Starter

Features implemented (starter):
- Admin (staff) can:
  - Login (use Django admin / createsuperuser)
  - Create Room
  - Update Room details
  - List all Reservations
  - Approve / Cancel Reservations
  - Logout

- Customer can:
  - Login (create user via admin or create registration manually)
  - View all available rooms
  - Make reservation
  - Receive notifications (stored in DB)
  - View reservation history
  - Logout

Database: SQLite (default Django DB file `db.sqlite3`)

Setup:
1. Create a virtualenv and install Django (see requirements.txt)
2. python manage.py migrate
3. python manage.py createsuperuser
4. python manage.py runserver
