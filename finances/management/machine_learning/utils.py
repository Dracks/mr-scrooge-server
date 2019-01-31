import random

from finances.management.models import Tag
from finances.core.models import RawDataSource


def normalize_name(name):
    while len(name)<256:
        name = name + " "
    return name

def load_data(**filter):
    data = RawDataSource.objects.filter(**filter)
    return [
        {
            "movement_name": normalize_name(rds.movement_name),
            "value": rds.value,
            "date": rds.date,
            "tags": [tag.name for tag in rds.tags.all()]
        }
        for rds in data
    ]

def load_tags():
    return {
        tag.pk: tag.name
        for tag in Tag.objects.all()
    }

def splitDataset(dataset, splitRatio):
    trainSize = int(len(dataset) * splitRatio)
    trainSet = []
    copy = list(dataset)
    while len(trainSet) < trainSize:
        index = random.randrange(len(copy))
        trainSet.append(copy.pop(index))
    return [trainSet, copy]