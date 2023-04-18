import os
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import IntegrityError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Loading initial data'

    def handle(self, *args, **options):
        path_to_json = os.path.join(
            settings.BASE_DIR,
            'data',
            'ingredients.json'
        )

        if not os.path.exists(path_to_json):
            raise CommandError('No file with initial data')

        with open(path_to_json, encoding='utf-8') as file:
            try:
                json_data = json.load(file)
                Ingredient.objects.bulk_create(
                    [Ingredient(**ingredient) for ingredient in json_data]
                )
            except IntegrityError:
                self.stdout.write(self.style.ERROR(
                        'Such ingredients already present in database'
                    )
                )
                return
            except Exception as error:
                raise CommandError(
                    'Error occured while loading itial data: ' + str(error)
                )

        self.stdout.write(self.style.SUCCESS('Data loaded'))
