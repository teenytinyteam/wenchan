from enum import Enum

import pandas as pd
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from chan.fractal import Fractal
from chan.layer import Interval, Layer
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
    return [{'symbol': '002594.SZ', 'name': '比亚迪'}]


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

    # 股价层
    source = Source(symbol)
    source_df = _load_layer_data(source, interval, date_format)
    if source_df is not None:
        data['source'] = source_df[['Date', 'Open', 'Close', 'Low', 'High',
                                    'MACD', 'Signal', 'Histogram']].values.tolist()

    # K线层
    stick = Stick(source)
    stick_df = _load_layer_data(stick, interval, date_format)
    if stick_df is not None:
        missing_dates = set(source_df['Date']) - set(stick_df['Date'])
        missing_data = pd.DataFrame({'Date': list(missing_dates)})
        for col in stick_df.columns:
            if col != 'Date':
                missing_data[col] = ''
        stick_df = pd.concat([stick_df, missing_data], ignore_index=True)
        stick_df = stick_df.sort_values(by='Date').reset_index(drop=True)
        data['stick'] = stick_df[['Date', 'Low', 'High']].values.tolist()

    # 分型层
    fractal = Fractal(stick)
    fractal_df = _load_layer_data(fractal, interval, date_format)
    if fractal_df is not None:
        data['fractal'] = fractal_df[['Date', 'Low', 'High']].values.tolist()

    # 笔层
    stroke = Stroke(fractal)
    stroke_df = _load_layer_data(stroke, interval, date_format)
    if stroke_df is not None:
        data['stroke'] = stroke_df[['Date', 'Low', 'High']].values.tolist()

    # 线段层
    segment = Segment(stroke)
    segment_df = _load_layer_data(segment, interval, date_format)
    if segment_df is not None:
        data['segment'] = segment_df[['Date', 'Low', 'High']].values.tolist()

    # 中枢层
    pivot = Pivot(segment)
    pivot_df = _load_layer_data(pivot, interval, date_format)
    if pivot_df is not None:
        pivot_df['High'] = pd.to_numeric(pivot_df['High'], errors='coerce')
        pivot_df['Low'] = pd.to_numeric(pivot_df['Low'], errors='coerce')
        pivot = pd.DataFrame(columns=['Start', 'End', 'Low', 'High'])
        for index in range(0, len(pivot_df), 2):
            start = pivot_df.iloc[index]
            end = pivot_df.iloc[index + 1]
            high = start['High'] if pd.notna(start['High']) else end['High']
            low = start['Low'] if pd.notna(start['Low']) else end['Low']
            pivot.loc[start.name] = [start['Date'], end['Date'], high, low]
        data['pivot'] = pivot.values.tolist()

    return data


# 加载一层数据
def _load_layer_data(layer: Layer, interval, date_format):
    layer.load_from_csv()
    data = layer.get_data(interval).dropna(how='all').fillna('').reset_index()
    if data is not None:
        data['Date'] = pd.to_datetime(data['Date'], utc=True)
        data['Date'] = data['Date'].dt.strftime(date_format)
    return data


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
