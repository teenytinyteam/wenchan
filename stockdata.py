from enum import Enum

import pandas as pd

from chan.fractal import Fractal
from chan.layer import Interval, Layer
from chan.pivot import StrokePivot, SegmentPivot
from chan.segment import Segment
from chan.source import Source
from chan.stick import Stick
from chan.stroke import Stroke

Y_M_D_H_M = '%Y-%m-%d %H:%M'
Y_M_D = '%Y-%m-%d'


class IntervalConfig(Enum):
    MIN_1 = {'name': '1分钟', 'format': Y_M_D_H_M}
    MIN_5 = {'name': '5分钟', 'format': Y_M_D_H_M}
    MIN_30 = {'name': '30分钟', 'format': Y_M_D_H_M}
    HOUR_1 = {'name': '1小时', 'format': Y_M_D_H_M}
    DAY_1 = {'name': '1天', 'format': Y_M_D}
    WEEK_1 = {'name': '1周', 'format': Y_M_D}
    MONTH_1 = {'name': '1月', 'format': Y_M_D}


class StockData:

    def __init__(self):
        self.symbol = None
        self.interval = None
        self.date_format = None

        self.data = {}
        self.source = None
        self.stick = None
        self.fractal = None
        self.stroke = None
        self.strokePivot = None
        self.segment = None
        self.segmentPivot = None

    def load(self, symbol, interval):
        self.symbol = symbol
        self.interval = Interval(interval)
        self.date_format = IntervalConfig[self.interval.name].value['format']

        source_df = self._load_source()
        self._load_stick(source_df)
        self._load_fractal()
        self._load_stroke()
        self._load_stroke_pivot()
        self._load_segment()
        self._load_segment_pivot()
        return self.data

    def _load_source(self):
        self.source = Source(self.symbol)
        source_df = self._load_layer_data(self.source)
        if source_df is not None:
            self.data['source'] = source_df[
                ['Date', 'Open', 'Close', 'Low', 'High',
                 'MACD', 'Signal', 'Histogram']].values.tolist()
        return source_df

    def _load_stick(self, source_df):
        self.stick = Stick(self.source)
        stick_df = self._load_layer_data(self.stick)
        if stick_df is not None:
            missing_dates = set(source_df['Date']) - set(stick_df['Date'])
            missing_data = pd.DataFrame({'Date': list(missing_dates)})
            for col in stick_df.columns:
                if col != 'Date':
                    missing_data[col] = ''
            stick_df = pd.concat([stick_df, missing_data], ignore_index=True)
            stick_df = stick_df.sort_values(by='Date').reset_index(drop=True)
            self.data['stick'] = stick_df[['Date', 'Low', 'High']].values.tolist()

    def _load_fractal(self):
        self.fractal = Fractal(self.stick)
        fractal_df = self._load_layer_data(self.fractal)
        if fractal_df is not None:
            self.data['fractal'] = fractal_df[['Date', 'Low', 'High']].values.tolist()

    def _load_stroke(self):
        self.stroke = Stroke(self.fractal)
        stroke_df = self._load_layer_data(self.stroke)
        if stroke_df is not None:
            self.data['stroke'] = stroke_df[['Date', 'Low', 'High']].values.tolist()

    def _load_stroke_pivot(self):
        self.strokePivot = StrokePivot(self.stroke)
        pivot_df = self._load_layer_data(self.strokePivot)
        if pivot_df is not None:
            self.data['stroke_pivot'] = self._format_pivot_data(pivot_df).values.tolist()

    def _load_segment(self):
        self.segment = Segment(self.stroke)
        segment_df = self._load_layer_data(self.segment)
        if segment_df is not None:
            self.data['segment'] = segment_df[['Date', 'Low', 'High']].values.tolist()
        return segment_df

    def _load_segment_pivot(self):
        self.segmentPivot = SegmentPivot(self.segment)
        pivot_df = self._load_layer_data(self.segmentPivot)
        if pivot_df is not None:
            self.data['segment_pivot'] = self._format_pivot_data(pivot_df).values.tolist()

    def _load_layer_data(self, layer: Layer):
        layer.load_from_csv()
        data = layer.get_data(self.interval).dropna(how='all').fillna('').reset_index()
        if data is not None:
            data['Date'] = pd.to_datetime(data['Date'], utc=True)
            data['Date'] = data['Date'].dt.strftime(self.date_format)
        return data

    @staticmethod
    def _format_pivot_data(pivot_df):
        pivot_df['High'] = pd.to_numeric(pivot_df['High'], errors='coerce')
        pivot_df['Low'] = pd.to_numeric(pivot_df['Low'], errors='coerce')
        df = pd.DataFrame(columns=['Start', 'End', 'Low', 'High'])
        for index in range(0, len(pivot_df), 2):
            start = pivot_df.iloc[index]
            end = pivot_df.iloc[index + 1]
            high = start['High'] if pd.notna(start['High']) else end['High']
            low = start['Low'] if pd.notna(start['Low']) else end['Low']
            df.loc[start.name] = [start['Date'], end['Date'], high, low]
        return df


if __name__ == '__main__':
    stockdata = StockData()
    stockdata.load("SQQQ", "1d")
