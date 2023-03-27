# What is this archive?

This monkey-themed KNN exercise has been written in python by tmickus and adapted by your 2021-22 PythonProg tutors for.

See `lab8-9-ecosystem.ipynb/` for the original instructions.

This code has been tested with python 3.8.

A sample visualization image is included under `data/`, along with the original data.

# How do I use it?

Install with:
```
$ python3 -m venv .venv && . .venv/bin/activate && pip3 install -r pip3.requirements.txt
```

Test with:
```
$ python3 src/tests.py
```

Run with (once your code is ready; feel free to test different functionalities of your code in-between as well):
```
$ python3 src/monkey_classif.py knn ./data/monkeys.csv ./data/output.csv --obs weight fur_color_int_r
$ python3 src/monkey_classif.py visualize ./data/output.csv weight fur_color_int_r
```
The first line runs the KNN, the second produces a visualization.

The main entry point `src/monkey_classif.py` also provides a help interface.
Try `python3 src/monkey_classif.py --help`, `python3 src/monkey_classif.py knn --help` or `python3 src/monkey_classif.py visualize --help`
