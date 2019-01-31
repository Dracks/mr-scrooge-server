import random
import math

from .utils import splitDataset

def normalize_row(row):
    data = [
        float(ord(c))
        for c in row["movement_name"]
    ]
    data.append(row["value"])
    movement_date = row["date"]
    data.append(float(movement_date.day))
    data.append(float(movement_date.month))
    data.append(float(movement_date.year))
    return data

def convert_data(data):
    return [{
            "key":  normalize_row(row),
            "values": row["tags"]
        }
        for row in data]

def separateByClass(dataset):
    separated = {}
    for data_row in dataset:
        vector = data_row["key"]
        for class_data in data_row["values"]:
            if class_data not in separated:
                separated[class_data] = []
            separated[class_data].append(vector)

    return {
        class_name: data
        for class_name, data in separated.items() if len(data)>2
    }

def mean(numbers):
    return sum(numbers)/float(len(numbers))

def stdev(numbers):
    avg = mean(numbers)
    variance = sum([pow(x-avg, 2) for x in numbers])/float(len(numbers)-1)
    return math.sqrt(variance)

def summarize(dataset):
    summaries = [(mean(attribute), stdev(attribute)) for attribute in zip(*dataset)]
    return summaries

def summarizeByClass(dataset):
    separated = separateByClass(dataset)
    return {
        classValue: summarize(instances)
        for classValue, instances in separated.items()
    }

def calculateProbability(x, mean, stdev):
    if stdev == 0:
        return 1
    exponent = math.exp(-(math.pow(x-mean,2)/(2*math.pow(stdev,2))))
    return (1 / (math.sqrt(2*math.pi) * stdev)) * exponent

def calculateClassProbabilities(summaries, inputVector):
    probabilities = {}
    maxValue = 0
    for classValue, classSummaries in summaries.items():
        p = 1
        for i in range(len(classSummaries)):
            mean, stdev = classSummaries[i]
            x = inputVector[i]
            p *= calculateProbability(x, mean, stdev)
        probabilities[classValue] = p
        if maxValue< p:
            maxValue = p
        
    return {
        classValue: probabilities/maxValue
        for classValue, probabilities in probabilities.items()
    }

def getPredictions(summaries, testSet):
    return [
        calculateClassProbabilities(summaries, test["key"])
        for test in testSet
    ]

def getAccuracy(testSet, predictions, boundary):
    pass


def test(data, boundary, splitRatio):
    dataset = convert_data(data)
    trainingSet, testSet = splitDataset(dataset, splitRatio)
    #print('Split {0} rows into train={1} and test={2} rows'.format(len(dataset), len(trainingSet), len(testSet)))
    summaries = summarizeByClass(trainingSet)

    predictions = getPredictions(summaries, testSet)
    #print(predictions)
    return getAccuracy(testSet, predictions, boundary)


