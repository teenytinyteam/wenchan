from chan.fractal import Fractal
from chan.pivot import StrokePivot, SegmentPivot
from chan.segment import Segment
from chan.source import Source
from chan.stick import Stick
from chan.stroke import Stroke


class StockList:

    def __init__(self):
        self.list = [{"symbol": "SQQQ", "name": "三倍做空纳指ETF-ProShares"},
                     {"symbol": "000001.SS", "name": "上证指数"}]

    def download(self):
        for stock in self.list:
            self._download_data(stock['symbol'])

    @staticmethod
    def _download_data(symbol):
        source = Source(symbol)
        source.generate()
        stick = Stick(source)
        stick.generate()
        fractal = Fractal(stick)
        fractal.generate()
        stroke = Stroke(fractal)
        stroke.generate()
        strokePivot = StrokePivot(stroke)
        strokePivot.generate()
        segment = Segment(stroke)
        segment.generate()
        segmentPivot = SegmentPivot(segment)
        segmentPivot.generate()


if __name__ == '__main__':
    stocklist = StockList()
    stocklist.download()