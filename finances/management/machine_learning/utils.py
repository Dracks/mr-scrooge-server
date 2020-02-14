import csv
import random

from finances.core.models import RawDataSource
from finances.management.models import Tag


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
            "tags": [tag.pk for tag in rds.tags.all()]
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

def generate_csv(name, data):
    list_tags = Tag.objects.all()
    tags_pk_list = [tag.pk for tag in list_tags]

    head = [
        "name",
        "value",
        "date"
    ]
    head.extend(["{}-{}".format(tag.pk, tag.name) for tag in list_tags])
    with open(name, 'w') as f:
        w = csv.writer(f)
        w.writerow([field.encode('ascii', 'ignore') for field in head])
        for mov in data:
            row = [
                mov['movement_name'].encode('ascii', 'ignore'),
                mov['value'],
                mov['date']
            ]
            enabled_tags = mov['tags']
            row.extend([tag in enabled_tags for tag in tags_pk_list])
            w.writerow(row)
