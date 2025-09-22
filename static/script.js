// Function to fetch data from the API
async function fetchData(symbol, interval) {
    try {
        const response = await fetch(`/api/${symbol}/${interval}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Failed to fetch data:", error);
        return null;
    }
}

// Update chart with new data
async function updateChart(symbol, interval) {
    const data = await fetchData(symbol, interval);
    let dates;
    if (data) {
        option.series[0].data = data.history.map(item => [
            item[1],
            item[2],
            item[3],
            item[4]
        ]);
        option.series[1].data = data.stick.map(item => [
            item[1],
            item[2],
            item[1],
            item[2]
        ]);
        option.series[2].data = data.fractal.map(item => item[1]);
        option.series[3].data = data.fractal.map(item => item[2]);
        option.series[4].data = data.stroke.map(item => item[1] == '' ? item[2] : item[1]);
        option.series[5].data = data.segment.map(item => item[1] == '' ? item[2] : item[1]);
        option.xAxis.data = data.history.map(item => item[0]);
        option.title.text = symbol;

        myChart.setOption(option, {
            notMerge: true,
            lazyUpdate: false,
            silent: false
        });
    } else {
        console.log("No data to update the chart.");
    }
}

const chartDom = document.getElementById('candlestick-chart');
const myChart = echarts.init(chartDom);

const option = {
    title: {
        text: '',
        left: 'center',
        textStyle: {
            fontSize: 18,
            fontWeight: 'bold'
        }
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'cross'
        },
        formatter: function (params) {
            const data = params[0].data;
            return `
                        <div style="font-weight: bold;">${params[0].axisValue}</div>
                        <div style="margin-top: 5px;">
                            Open: $${data[1].toFixed(2)}<br/>
                            Close: $${data[2].toFixed(2)}<br/>
                            Low: $${data[3].toFixed(2)}<br/>
                            High: $${data[4].toFixed(2)}
                        </div>
                    `;
        }
    },
    xAxis: {
        type: 'category',
        data: [],
        scale: true,
        boundaryGap: false,
        axisLine: {onZero: false},
        splitLine: {show: false},
        min: 'dataMin',
        max: 'dataMax'
    },
    yAxis: {
        scale: true,
        splitArea: {
            show: true
        },
        axisLabel: {
            formatter: '${value}'
        }
    },
    dataZoom: [
        {
            type: 'inside',
            start: 50,
            end: 100
        },
        {
            show: true,
            type: 'slider',
            top: '90%',
            start: 50,
            end: 100
        }
    ],
    series: [
        {
            name: 'Stock Price',
            type: 'candlestick',
            data: [],
            itemStyle: {
                color: '#06B83F',        // Color for bullish candles (close > open)
                color0: '#E53E3E',       // Color for bearish candles (close < open)
                borderColor: '#06B83F',   // Border color for bullish candles
                borderColor0: '#E53E3E'   // Border color for bearish candles
            }
        },
        {
            name: 'Stick',
            type: 'candlestick',
            data: [],
            itemStyle: {
                color: '#E0A800',
                color0: '#E0A800',
                borderColor: '#FFC107',
                borderColor0: '#FFC107'
            }
        },
        {
            name: 'Bottom Fractal',
            type: 'scatter',
            data: [],
            symbol: 'triangle',
            symbolSize: 8,
            symbolRotate: 0,
            symbolOffset: [0, 8],
            itemStyle: {
                color: '#E53E3E',
                borderColor: '#E53E3E',
                borderWidth: 1
            }
        },
        {
            name: 'Top Fractal',
            type: 'scatter',
            data: [],
            symbol: 'triangle',
            symbolSize: 8,
            symbolRotate: 180,
            symbolOffset: [0, -8],
            itemStyle: {
                color: '#06B83F',
                borderColor: '#06B83F',
                borderWidth: 1
            }
        },
        {
            name: 'Stroke',
            type: 'line',
            data: [],
            connectNulls: true,
            symbol: 'circle',
            symbolSize: 4,
            lineStyle: {
                color: '#4A90E2',
                width: 2
            },
            itemStyle: {
                color: '#4A90E2',
                borderColor: '#2E5C8A',
                borderWidth: 1
            }
        },
        {
            name: 'Segment',
            type: 'line',
            data: [],
            connectNulls: true,
            symbol: 'circle',
            symbolSize: 4,
            lineStyle: {
                color: '#FF6B35',
                width: 2
            },
            itemStyle: {
                color: '#FF6B35',
                borderColor: '#E55A2B',
                borderWidth: 1
            }
        }
    ]
};

myChart.setOption(option);

updateChart('AAPL', '1d');

// Make chart responsive
window.addEventListener('resize', function () {
    myChart.resize();
});

// Add some interactivity
myChart.on('click', function (params) {
    if (params.componentType === 'series') {
        const dataIndex = params.dataIndex;
        const dates = option.xAxis.data;
        const data = params.data;
        console.log(`Clicked on ${dates[dataIndex]}: Open=${data[1]}, Close=${data[2]}, Low=${data[3]}, High=${data[4]}`);
    }
});