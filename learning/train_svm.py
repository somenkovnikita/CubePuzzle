import argparse
import os
import random

import cv2
import numpy as np
from sklearn.externals import joblib
from sklearn.metrics import classification_report
from sklearn.svm import LinearSVC

from vision.letterrecognizers import SVMLetterRecognizer


def prepare_images(paths):
    for p in paths:
        i = cv2.imread(p)
        if i is None:
            pass
    images = map(cv2.imread, paths)
    processing = SVMLetterRecognizer.preprocessing
    i = map(processing, images)
  
    return i           


def prepare_classes(classes):
    return map(int, classes)


def load_dataset(dataset_dir):
    import random
    filename = os.path.join(dataset_dir, 'marked.list')
    with open(filename) as paths:
        lines = paths.readlines()
        random.shuffle(lines)
        fns, cls = zip(*map(str.split, lines))

    def j(x):
        return os.path.join(dataset_dir, x)
    return map(j, fns), cls


def prepare_inputs_outputs(config):
    print 'Reading dataset...'

    paths, classes = load_dataset(config)

    inputs = prepare_images(paths)
    outputs = prepare_classes(classes)

    idcs = range(len(inputs))
    random.shuffle(idcs)
    random_inputs = [inputs[i] for i in idcs]
    random_outputs = [outputs[i] for i in idcs]

    return random_inputs, np.array(random_outputs)


if __name__ == '__main__' :
    DEFAULT_CONFIG = os.path.join('config', 'letter_recognizer.svm')

    parser = argparse.ArgumentParser(description='Train svm model')

    parser.add_argument('-i', '--training_set', required=True,
                        help='Directory with training set with market.list')
    parser.add_argument('-t', '--test_set',
                        help='Directory with test set with market.list')
    parser.add_argument('-o', '--output', default=DEFAULT_CONFIG,
                        help='Specify file path to save model')

    print 'Reading dataset...'
    args = parser.parse_args()

    model = LinearSVC()
    inputs, outputs = prepare_inputs_outputs(args.training_set)

    model.fit(inputs, outputs)

    if args.test_set:
        ins, outs = prepare_inputs_outputs(args.test_set)
        predicts = model.predict(ins)
        print classification_report(outs, predicts)

    joblib.dump(model, args.output)
