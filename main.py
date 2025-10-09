import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from chan.layer import Interval
from stockdata import IntervalConfig, StockData
from stocklist import StockList

app = FastAPI()
app.mount(path='/static',
          app=StaticFiles(directory='static'),
          name='static')
templates = Jinja2Templates(directory='templates')


@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    params = {'request': request}
    return templates.TemplateResponse('index.html', params)


@app.get('/api/stocks')
async def get_stocks():
    return StockList().list


@app.get('/api/periods')
async def get_periods():
    return [{'id': iv.value,
             'name': IntervalConfig[iv.name].value['name']} for iv in Interval]


@app.get('/api/{symbol}/{interval}')
async def get_data(symbol: str, interval: str):
    return StockData().load(symbol, interval)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
