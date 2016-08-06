# cloud-compare
Cloud Comparison Tool. Compare public clouds on price and performance.

Very early. Working on cloud database.

Environment: python 2.7, sqlite3

Initial setup (create empty database):
   $ python manage.py makemigrations pricing
   $ python manage.py migrate

   To start from scratch (everthing);
   $ rm db.sqlite3 pricing/migrations/*

   To empty the database but not delete (you'll be asked if it's OK)
   $ python manage.py flush

Populate database (if you this twice you'll end up with 2 copies of every record)
   To populate with data from Google:
   $ python manage.py gcp_populate

   To populate with data from Amazon:
   $ python manage.py aws_populate

Run test server:
   $ python manage.py runserver
