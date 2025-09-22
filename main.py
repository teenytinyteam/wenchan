import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from source import *

app = FastAPI()
app.mount(path='/static',
          app=StaticFiles(directory='static'),
          name='static')
templates = Jinja2Templates(directory='templates')


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return await _load_data(request)


async def _load_data(request):
    params = {
        'request': request
    }
    return templates.TemplateResponse('index.html', params)


@app.get("/api/{symbol}/{interval}")
async def get_data(symbol: str, interval: str):
    data = {"symbol": symbol, "interval": interval}

    history = History(symbol, auto_load=False, auto_save=False)
    load_history_from_csv(history)
    history_df = history.get_data(interval).dropna(how='all').fillna('').reset_index()
    if history_df is not None:
        history_df['Date'] = pd.to_datetime(history_df['Date'], utc=True)
        history_df['Date'] = history_df['Date'].dt.strftime('%Y-%m-%d')
        data["history"] = history_df[['Date', 'Open', 'Close', 'Low', 'High']].values.tolist()

    stick = Stick(history, auto_save=False)
    load_stick_from_csv(stick)
    stick_df = stick.get_data(interval).dropna(how='all').fillna('').reset_index()
    if stick_df is not None:
        stick_df['Date'] = pd.to_datetime(stick_df['Date'], utc=True)
        stick_df['Date'] = stick_df['Date'].dt.strftime('%Y-%m-%d')

        missing_dates = set(history_df['Date']) - set(stick_df['Date'])
        missing_data = pd.DataFrame({'Date': list(missing_dates)})
        for col in stick_df.columns:
            if col != 'Date':
                missing_data[col] = ''
        stick_df = pd.concat([stick_df, missing_data], ignore_index=True)
        stick_df = stick_df.sort_values(by='Date').reset_index(drop=True)

        data["stick"] = stick_df[['Date', 'Low', 'High']].values.tolist()

    fractal = Fractal(stick, auto_save=False)
    load_fractal_from_csv(fractal)
    fractal_df = fractal.get_data(interval).dropna(how='all').fillna('').reset_index()
    if fractal_df is not None:
        fractal_df['Date'] = pd.to_datetime(fractal_df['Date'], utc=True)
        fractal_df['Date'] = fractal_df['Date'].dt.strftime('%Y-%m-%d')

        missing_dates = set(history_df['Date']) - set(fractal_df['Date'])
        missing_data = pd.DataFrame({'Date': list(missing_dates)})
        for col in fractal_df.columns:
            if col != 'Date':
                missing_data[col] = ''
        fractal_df = pd.concat([fractal_df, missing_data], ignore_index=True)
        fractal_df = fractal_df.sort_values(by='Date').reset_index(drop=True)

        data["fractal"] = fractal_df[['Date', 'Low', 'High']].values.tolist()

    stroke = Stroke(fractal, auto_save=False)
    load_stroke_from_csv(stroke)
    stroke_df = stroke.get_data(interval).dropna(how='all').fillna('').reset_index()
    if stroke_df is not None:
        stroke_df['Date'] = pd.to_datetime(stroke_df['Date'], utc=True)
        stroke_df['Date'] = stroke_df['Date'].dt.strftime('%Y-%m-%d')

        missing_dates = set(history_df['Date']) - set(stroke_df['Date'])
        missing_data = pd.DataFrame({'Date': list(missing_dates)})
        for col in stroke_df.columns:
            if col != 'Date':
                missing_data[col] = ''
        stroke_df = pd.concat([stroke_df, missing_data], ignore_index=True)
        stroke_df = stroke_df.sort_values(by='Date').reset_index(drop=True)

        data["stroke"] = stroke_df[['Date', 'Low', 'High']].values.tolist()

    segment = Segment(stroke, auto_save=False)
    load_segment_from_csv(segment)
    segment_df = segment.get_data(interval).dropna(how='all').fillna('').reset_index()
    if segment_df is not None:
        segment_df['Date'] = pd.to_datetime(segment_df['Date'], utc=True)
        segment_df['Date'] = segment_df['Date'].dt.strftime('%Y-%m-%d')

        missing_dates = set(history_df['Date']) - set(segment_df['Date'])
        missing_data = pd.DataFrame({'Date': list(missing_dates)})
        for col in segment_df.columns:
            if col != 'Date':
                missing_data[col] = ''
        segment_df = pd.concat([segment_df, missing_data], ignore_index=True)
        segment_df = segment_df.sort_values(by='Date').reset_index(drop=True)

        data["segment"] = segment_df[['Date', 'Low', 'High']].values.tolist()

    return data


@app.get("/api/history/{symbol}/{interval}")
async def get_history(symbol: str, interval: str):
    history = History(symbol, auto_load=False, auto_save=False)
    load_history_from_csv(history)
    data = history.get_data(interval)
    data = data.dropna(how='all')
    data = data.fillna('')
    if data is not None:
        return data.to_dict(orient='records')
    else:
        return {"error": "No data found for the given symbol and interval."}


@app.get("/api/stick/{symbol}/{interval}")
async def get_stick(symbol: str, interval: str):
    history = History(symbol, auto_load=False, auto_save=False)
    stick = Stick(history, auto_save=False)
    load_stick_from_csv(stick)
    data = stick.get_data(interval)
    data = data.dropna(how='all')
    data = data.fillna('')
    if data is not None:
        return data.to_dict(orient='records')
    else:
        return {"error": "No data found for the given symbol and interval."}


@app.get("/api/fractal/{symbol}/{interval}")
async def get_fractal(symbol: str, interval: str):
    history = History(symbol, auto_load=False, auto_save=False)
    stick = Stick(history, auto_save=False)
    fractal = Fractal(stick, auto_save=False)
    load_fractal_from_csv(fractal)
    data = fractal.get_data(interval)
    data = data.dropna(how='all')
    data = data.fillna('')
    if data is not None:
        return data.to_dict(orient='records')
    else:
        return {"error": "No data found for the given symbol and interval."}


@app.get("/api/stroke/{symbol}/{interval}")
async def get_stroke(symbol: str, interval: str):
    history = History(symbol, auto_load=False, auto_save=False)
    stick = Stick(history, auto_save=False)
    fractal = Fractal(stick, auto_save=False)
    stroke = Stroke(fractal, auto_save=False)
    load_stroke_from_csv(stroke)
    data = stroke.get_data(interval)
    data = data.dropna(how='all')
    data = data.fillna('')
    if data is not None:
        return data.to_dict(orient='records')
    else:
        return {"error": "No data found for the given symbol and interval."}


@app.get("/api/segment/{symbol}/{interval}")
async def get_segment(symbol: str, interval: str):
    history = History(symbol, auto_load=False, auto_save=False)
    stick = Stick(history, auto_save=False)
    fractal = Fractal(stick, auto_save=False)
    stroke = Stroke(fractal, auto_save=False)
    segment = Segment(stroke, auto_save=False)
    load_segment_from_csv(segment)
    data = segment.get_data(interval)
    data = data.dropna(how='all')
    data = data.fillna('')
    if data is not None:
        return data.to_dict(orient='records')
    else:
        return {"error": "No data found for the given symbol and interval."}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
