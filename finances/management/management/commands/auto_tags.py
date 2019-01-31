from django.core.management.base import BaseCommand
from datetime import datetime, timedelta


from finances.management.machine_learning import utils, bayesian


today = datetime.today()

class Command(BaseCommand):
    help = "Test the auto linking tags with Machine Learning"

    def handle(self, *args, **options):
        long_ago = today + timedelta(days=-90)
        dataset = utils.load_data(date__gte=long_ago)
        bayesian.test(dataset, 0.5, 0.67)
        