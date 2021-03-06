# cloud-compare

# Compare public clouds on price and performance.

Very early. Working on cloud database.

Environment: python 2.7, sqlite3, django 1.9
             pep8 to enforce coding standard

## Test It:

   ```$ python manage.py test```

## Initial setup (create empty database):

   ```$ python manage.py makemigrations pricing```

   ```$ python manage.py migrate```

## To start from scratch (everthing);

   ```$ rm db.sqlite3 pricing/migrations/*```

   To empty the database but not delete (you'll be asked if it's OK)

   ```$ python manage.py flush```

## Populate database (if you this twice you'll end up with 2 copies of every record)

### Database population is perfomed in two steps:

* Scrape data from the remote site into a local directory.
* Ingest data files from local directory into the database.

Both operations are avilable through the ```manage.py``` 

   To scrape data from Amazon:

   ```$ python manage.py scrape --aws <directory>```
   (the directory must exist and be empty)

   To scrape data from Google:

   ```$ python manage.py scrape --gcp <directory>```
   (the directory must exist and be empty)

   To ingest scraped data into master DB:

   ```$ python manage.py ingest <directory>```

Running ```ingest``` more than one time results in multiple entries in the 
master database.

   To extract data from master DB to UI DB's

   ```$ python manage.py extract```

Running ```extract``` more than one time results in multiple entries in the 
UI database.

## Run test server:

   ```$ python manage.py runserver```

   The command prints the URL to connect to.
