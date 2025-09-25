import pandas as pd
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from chan.fractal import Fractal
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
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return await _load_data(request)


# 加载数据
async def _load_data(request):
    params = {
        'request': request
    }
    return templates.TemplateResponse('index.html', params)


# 数据API路由，返回一个时间周期的JSON数据
@app.get("/api/{symbol}/{interval}")
async def get_data(symbol: str, interval: str):
    data = {}

    # 原始数据
    history = Source(symbol, auto_load=False, auto_save=False)
    history_df = history.get_data(interval).dropna(how='all').fillna('').reset_index()
    if history_df is not None:
        # 处理数据格式
        history_df['Date'] = pd.to_datetime(history_df['Date'], utc=True)
        history_df['Date'] = history_df['Date'].dt.strftime('%Y-%m-%d')
        data["history"] = history_df[['Date', 'Open', 'Close', 'Low', 'High']].values.tolist()

    # 残论K线
    stick = Stick(history, auto_save=False)
    stick_df = stick.get_data(interval).dropna(how='all').fillna('').reset_index()
    if stick_df is not None:
        # 处理数据格式
        stick_df['Date'] = pd.to_datetime(stick_df['Date'], utc=True)
        stick_df['Date'] = stick_df['Date'].dt.strftime('%Y-%m-%d')
        # 和原始数据对齐
        missing_dates = set(history_df['Date']) - set(stick_df['Date'])
        missing_data = pd.DataFrame({'Date': list(missing_dates)})
        for col in stick_df.columns:
            if col != 'Date':
                missing_data[col] = ''
        stick_df = pd.concat([stick_df, missing_data], ignore_index=True)
        stick_df = stick_df.sort_values(by='Date').reset_index(drop=True)

        data["stick"] = stick_df[['Date', 'Low', 'High']].values.tolist()

    # 缠论分型
    fractal = Fractal(stick, auto_save=False)
    fractal_df = fractal.get_data(interval).dropna(how='all').fillna('').reset_index()
    if fractal_df is not None:
        # 处理数据格式
        fractal_df['Date'] = pd.to_datetime(fractal_df['Date'], utc=True)
        fractal_df['Date'] = fractal_df['Date'].dt.strftime('%Y-%m-%d')
        # 和原始数据对齐
        missing_dates = set(history_df['Date']) - set(fractal_df['Date'])
        missing_data = pd.DataFrame({'Date': list(missing_dates)})
        for col in fractal_df.columns:
            if col != 'Date':
                missing_data[col] = ''
        fractal_df = pd.concat([fractal_df, missing_data], ignore_index=True)
        fractal_df = fractal_df.sort_values(by='Date').reset_index(drop=True)
        data["fractal"] = fractal_df[['Date', 'Low', 'High']].values.tolist()

    # 缠论笔
    stroke = Stroke(fractal, auto_save=False)
    stroke_df = stroke.get_data(interval).dropna(how='all').fillna('').reset_index()
    if stroke_df is not None:
        # 处理数据格式
        stroke_df['Date'] = pd.to_datetime(stroke_df['Date'], utc=True)
        stroke_df['Date'] = stroke_df['Date'].dt.strftime('%Y-%m-%d')
        # 和原始数据对齐
        missing_dates = set(history_df['Date']) - set(stroke_df['Date'])
        missing_data = pd.DataFrame({'Date': list(missing_dates)})
        for col in stroke_df.columns:
            if col != 'Date':
                missing_data[col] = ''
        stroke_df = pd.concat([stroke_df, missing_data], ignore_index=True)
        stroke_df = stroke_df.sort_values(by='Date').reset_index(drop=True)
        data["stroke"] = stroke_df[['Date', 'Low', 'High']].values.tolist()

    # 缠论线段
    segment = Segment(stroke, auto_save=False)
    segment_df = segment.get_data(interval).dropna(how='all').fillna('').reset_index()
    if segment_df is not None:
        # 处理数据格式
        segment_df['Date'] = pd.to_datetime(segment_df['Date'], utc=True)
        segment_df['Date'] = segment_df['Date'].dt.strftime('%Y-%m-%d')
        # 和原始数据对齐
        missing_dates = set(history_df['Date']) - set(segment_df['Date'])
        missing_data = pd.DataFrame({'Date': list(missing_dates)})
        for col in segment_df.columns:
            if col != 'Date':
                missing_data[col] = ''
        segment_df = pd.concat([segment_df, missing_data], ignore_index=True)
        segment_df = segment_df.sort_values(by='Date').reset_index(drop=True)
        data["segment"] = segment_df[['Date', 'Low', 'High']].values.tolist()

    return data


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
