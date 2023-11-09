import io
import logging
from csv import DictReader

from django.core.management import BaseCommand
from recipes.models import Ingredient

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the child data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


def main_fill():
    logging.info("Main loading")
    if Ingredient.objects.exists():
        logging.warning("child data already loaded...exiting.")
        raise Exception(ALREDY_LOADED_ERROR_MESSAGE)

    logging.info("Loading - data a table - Ingredient")
    for row in DictReader(
        io.open("static/data/ingredients.csv", mode="r", encoding="utf-8")
    ):
        Ingredient.objects.get_or_create(
            name=row["name"],
            measurement_unit=row["measurement_unit"],
        )
    logging.info("Successfully - loading data table - Ingredient")


class Command(BaseCommand):
    help = "Loads data from children.csv"

    def handle(self, *args, **options):
        logging.info("----------------------------------------")
        main_fill()
        logging.info("----------------------------------------")
        return
