import os

import pandas as pd

from chan.fractal import Fractal
from chan.history import Interval, History
from chan.segment import Segment
from chan.stick import Stick
from chan.stroke import Stroke


def load_history_from_csv(history: History):
    folder = f'data/{history.symbol}'
    for interval in Interval:
        file_path = f'{folder}/history_{interval.value[0]}.csv'
        if os.path.exists(file_path):
            try:
                data = pd.read_csv(file_path, index_col=0, parse_dates=True)
                history.data[interval.value[0]] = data
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        else:
            print(f"File {file_path} does not exist.")


def load_stick_from_csv(stick: Stick):
    folder = f'data/{stick.history.symbol}'
    for interval in Interval:
        file_path = f'{folder}/stick_{interval.value[0]}.csv'
        if os.path.exists(file_path):
            try:
                data = pd.read_csv(file_path, index_col=0, parse_dates=True)
                stick.data[interval.value[0]] = data
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        else:
            print(f"File {file_path} does not exist.")


def load_fractal_from_csv(fractal: Fractal):
    folder = f'data/{fractal.stick.history.symbol}'
    for interval in Interval:
        file_path = f'{folder}/fractal_{interval.value[0]}.csv'
        if os.path.exists(file_path):
            try:
                data = pd.read_csv(file_path, index_col=0, parse_dates=True)
                fractal.data[interval.value[0]] = data
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        else:
            print(f"File {file_path} does not exist.")


def load_stroke_from_csv(stroke: Stroke):
    folder = f'data/{stroke.fractal.stick.history.symbol}'
    for interval in Interval:
        file_path = f'{folder}/stroke_{interval.value[0]}.csv'
        if os.path.exists(file_path):
            try:
                data = pd.read_csv(file_path, index_col=0, parse_dates=True)
                stroke.data[interval.value[0]] = data
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        else:
            print(f"File {file_path} does not exist.")


def load_segment_from_csv(segment: Segment):
    folder = f'data/{segment.stroke.fractal.stick.history.symbol}'
    for interval in Interval:
        file_path = f'{folder}/segment_{interval.value[0]}.csv'
        if os.path.exists(file_path):
            try:
                data = pd.read_csv(file_path, index_col=0, parse_dates=True)
                segment.data[interval.value[0]] = data
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        else:
            print(f"File {file_path} does not exist.")
