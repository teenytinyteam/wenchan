from enum import Enum

import numpy as np
import pandas as pd
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from chan.fractal import Fractal
from chan.layer import Interval
from chan.pivot import Pivot
from chan.segment import Segment
from chan.source import Source
from chan.stick import Stick
from chan.stroke import Stroke

# 初始化FastAPI
app = FastAPI()
app.mount(path='/static',
          app=StaticFiles(directory='static'),
          name='static')
templates = Jinja2Templates(directory='templates')


# 根路由，返回HTML页面
@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    return await _load_data(request)


# 加载数据
async def _load_data(request):
    params = {
        'request': request
    }
    return templates.TemplateResponse('index.html', params)


# 数据API路由，返回股票列表
@app.get('/api/stocks')
async def get_stocks():
    return [{'symbol': 'AAPL', 'name': '苹果'}]


class IntervalConfig(Enum):
    MIN_1 = {'name': '1分钟', 'format': '%Y-%m-%d %H:%M'}
    MIN_5 = {'name': '5分钟', 'format': '%Y-%m-%d %H:%M'}
    MIN_30 = {'name': '30分钟', 'format': '%Y-%m-%d %H:%M'}
    HOUR_1 = {'name': '1小时', 'format': '%Y-%m-%d %H:%M'}
    DAY_1 = {'name': '1天', 'format': '%Y-%m-%d'}
    WEEK_1 = {'name': '1周', 'format': '%Y-%m-%d'}
    MONTH_1 = {'name': '1月', 'format': '%Y-%m-%d'}


# 数据API路由，返回周期列表
@app.get('/api/periods')
async def get_stocks():
    return [{'id': iv.value, 'name': IntervalConfig[iv.name].value['name']} for iv in Interval]


# 数据API路由，返回一个时间周期的JSON数据
@app.get('/api/{symbol}/{interval}')
async def get_data(symbol: str, interval: str):
    data = {}
    interval = Interval(interval)
    date_format = IntervalConfig[interval.name].value['format']

    # 原始数据
    source = Source(symbol)
    source.load_from_csv()
    source_df = source.get_data(interval).dropna(how='all').fillna('').reset_index()
    if source_df is not None:
        source_df['Date'] = pd.to_datetime(source_df['Date'], utc=True)
        source_df['Date'] = source_df['Date'].dt.strftime(date_format)
        data['source'] = source_df[['Date', 'Open', 'Close', 'Low', 'High']].values.tolist()

    # 残论K线
    stick = Stick(source)
    stick.load_from_csv()
    stick_df = stick.get_data(interval).dropna(how='all').fillna('').reset_index()
    if stick_df is not None:
        stick_df['Date'] = pd.to_datetime(stick_df['Date'], utc=True)
        stick_df['Date'] = stick_df['Date'].dt.strftime(date_format)

        missing_dates = set(source_df['Date']) - set(stick_df['Date'])
        missing_data = pd.DataFrame({'Date': list(missing_dates)})
        for col in stick_df.columns:
            if col != 'Date':
                missing_data[col] = ''
        stick_df = pd.concat([stick_df, missing_data], ignore_index=True)
        stick_df = stick_df.sort_values(by='Date').reset_index(drop=True)

        data['stick'] = stick_df[['Date', 'Low', 'High', 'Low', 'High']].values.tolist()

    # 缠论分型
    fractal = Fractal(stick)
    fractal.load_from_csv()
    fractal_df = fractal.get_data(interval).dropna(how='all').fillna('').reset_index()
    if fractal_df is not None:
        fractal_df['Date'] = pd.to_datetime(fractal_df['Date'], utc=True)
        fractal_df['Date'] = fractal_df['Date'].dt.strftime(date_format)
        data['fractal'] = fractal_df[['Date', 'Low', 'High']].values.tolist()

    # 缠论笔
    stroke = Stroke(fractal)
    stroke.load_from_csv()
    stroke_df = stroke.get_data(interval).dropna(how='all').fillna('').reset_index()
    if stroke_df is not None:
        stroke_df['Date'] = pd.to_datetime(stroke_df['Date'], utc=True)
        stroke_df['Date'] = stroke_df['Date'].dt.strftime(date_format)
        data['stroke'] = stroke_df[['Date', 'Low', 'High']].values.tolist()

    # 缠论线段
    segment = Segment(stroke)
    segment.load_from_csv()
    segment_df = segment.get_data(interval).dropna(how='all').fillna('').reset_index()
    if segment_df is not None:
        segment_df['Date'] = pd.to_datetime(segment_df['Date'], utc=True)
        segment_df['Date'] = segment_df['Date'].dt.strftime(date_format)
        data['segment'] = segment_df[['Date', 'Low', 'High']].values.tolist()

    # 缠论中枢
    pivot = Pivot(segment)
    pivot.load_from_csv()
    pivot_df = pivot.get_data(interval).dropna(how='all').reset_index()
    if pivot_df is not None:
        pivot_df['Date'] = pd.to_datetime(pivot_df['Date'], utc=True)
        pivot_df['Date'] = pivot_df['Date'].dt.strftime(date_format)

        pivot = pd.DataFrame(columns=['Start', 'End', 'High', 'Low'])
        for index in range(0, len(pivot_df), 2):
            start = pivot_df.iloc[index]
            end = pivot_df.iloc[index + 1]
            high = end['High'] if np.isnan(start['High']) else start['High']
            low = end['Low'] if np.isnan(start['Low']) else start['Low']
            pivot.loc[start.name] = [start['Date'], end['Date'], high, low]

        data['pivot'] = pivot.values.tolist()

    return data


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
