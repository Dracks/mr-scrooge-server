from django.core.management.base import BaseCommand
from datetime import datetime, timedelta


from finances.management.machine_learning import utils, bayesian, keras


today = datetime.today()

class Command(BaseCommand):
    help = "Test the auto linking tags with Machine Learning"
    def add_arguments(self, parser):
        parser.add_argument('-b', '--bayesian', default=False, action="store_true", help="Run bayesian test")
        parser.add_argument('-k', '--keras', default=False, action="store_true", help="Run Keras tests")

    def handle(self, *args, **options):
        long_ago = today + timedelta(days=-90)
        dataset = utils.load_data(date__gte=long_ago)
        if options.get('bayesian'):
            bayesian.test(dataset, 0.5, 0.67)
        if options.get('keras'):
            tags = utils.load_tags()
            #print(tags)
            keras.test(dataset, 2, 0.67)
        