from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from finances.management.machine_learning import bayesian, keras, utils

today = datetime.today()

class Command(BaseCommand):
    help = "Test the auto linking tags with Machine Learning"
    def add_arguments(self, parser):
        parser.add_argument('-b', '--bayesian', default=False, action="store_true", help="Run bayesian test")
        parser.add_argument('-k', '--keras', default=False, action="store_true", help="Run Keras tests")
        parser.add_argument('-d', '--donut', default=False, action="store_true", help="Run Donuts tests")
        parser.add_argument('-c', '--csv', default=False, action="store_true", help="Generate a csv file with all the data")

    def handle(self, *args, **options):
        long_ago = today + timedelta(days=-365)
        dataset = utils.load_data(date__gte=long_ago)
        print(today, long_ago, len(dataset))
        if options.get('bayesian'):
            bayesian.test(dataset, 0.5, 0.67)
        if options.get('keras'):
            print(keras.test(dataset, 2, 0.69))
            """tags = utils.load_tags()
            result = {}
            for tag_pk, name in tags.items():
                result[name] = keras.test(dataset, tag_pk, 0.75)

            print(result)
            """
        if options.get('csv'):
            utils.generate_csv('test.csv', dataset)
        if options.get('donut'):
            keras.donut_test()
