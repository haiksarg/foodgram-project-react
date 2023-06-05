import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Loads data from ingredients.csv'

    def handle(self, *args, **options):

        print('Loading ingredients data')

        try:
            with open('../data/ingredients.csv',
                      'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for name, unit in reader:
                    _, boool = Ingredient.objects.get_or_create(
                        name=name, measurement_unit=unit
                    )
                    if not boool:
                        print(f'Ingredient {name} with measurement_unit '
                              f'{unit} already exists')
                print('The data from the ingredients.csv '
                      'has been uploaded successfully')
        except IOError as er:
            print(f'Could not open ingredients.csv: {er}')
