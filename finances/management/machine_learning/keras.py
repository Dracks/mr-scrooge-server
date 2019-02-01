from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
import keras
import numpy as np

from .utils import splitDataset

MINIMUM_VALUES = 3

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
    return np.array(data)

def compare(reals, results):
    errors = 0.0
    size = len(results)
    for i in range(size):
        pred = results[i]
        real = reals[i]
        if pred != real:
            errors += 1
    return 1-(errors/size)

def getData(dataset, tag):
    in_values = [ normalize_row(row) for row in dataset]
    out_values = [ int(tag in row["tags"]) for row in dataset]
    return np.array(in_values), np.array(out_values)

def build():
    model = Sequential()
    model.add(Dense(300, input_dim=260, activation='relu'))
    model.add(Dense(250, activation='relu'))
    model.add(Dense(80, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def test(dataset, tag, splitRatio):
    trainingSet, testSet = splitDataset(dataset, splitRatio)

    training_in, training_out = getData(trainingSet, tag)
    true_values_len = len([ value for value in training_out if value==1])
    if true_values_len < MINIMUM_VALUES or len(training_out)-true_values_len < MINIMUM_VALUES:
        return ("No values", true_values_len)

    model = build()

    model.fit(training_in, training_out, epochs=20, batch_size=32, verbose=0)

    test_in, test_out = getData(testSet, tag)

    predictions = model.predict(test_in)
    # round predictions
    rounded = [round(x[0]) for x in predictions]

    return (compare(rounded, test_out), true_values_len, len(training_out)-true_values_len)

def donut_test():
    def donut_fn(x,y):
        d = x*x+y*y
        if d>0.2 and d<0.7:
            return 1
        else:
            return 0
    model = Sequential()
    model.add(Dense(12, input_dim=2, activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    # Generate dummy data
    data = np.random.random((300, 2))
    labels = np.array([[donut_fn(row[0], row[1])] for row in data])
    #labels = np.random.randint(10, size=(1000, 1))

    # Train the model, iterating on the data in batches of 32 samples
    model.fit(data, labels, epochs=100, batch_size=32)

    test = np.random.random((10, 2))
    # calculate predictions
    predictions = model.predict(test)
    # round predictions
    rounded = [round(x[0]) for x in predictions]

    print(compare([donut_fn(row[0], row[1]) for row in test], rounded))
    print([donut_fn(row[0], row[1]) for row in test])