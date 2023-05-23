import csv

from django.core.management import BaseCommand
# Import the model
from recipes.models import Ingredient

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the  data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads data from ingredients.csv"

    def handle(self, *args, **options):

        # Show this if the data already exist in the database
        if Ingredient.objects.exists():
            print('Ingredient data already loaded...exiting.')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        # Show this before loading the data into the database
        print("Loading ingredients data")

        # Code to load the data into database
        with open('../data/ingredients.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row[0], measurement_unit=row[1]
                )
        print('The data from the ingredients.csv '
              'has been uploaded successfully')
