const chartDom = document.getElementById('candlestick-chart');
let myChart = echarts.init(chartDom);

let chanData;
let layers;

function showLoading() {
    if (chartDom && myChart) {
        myChart.showLoading('default', {
            text: '加载中...',
            color: '#4A90E2',
            textColor: '#000',
            maskColor: 'rgba(255, 255, 255, 0.8)',
            zlevel: 0
        });
    }
}

function hideLoading() {
    if (myChart) {
        myChart.hideLoading();
    }
}

async function fetchData(symbol, interval) {
    try {
        showLoading();
        const response = await fetch(`/api/${symbol}/${interval}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Failed to fetch data:", error);
        return null;
    } finally {
        hideLoading();
    }
}

const option = {
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'cross'
        },
        formatter: function (params) {
            const data = params[0].data;
            const date = params[0].axisValueLabel;
            return `
                        <div style="font-weight: bold;">${date}</div>
                        <div style="margin-top: 5px;">
                            开盘：$${data[1].toFixed(4)}<br/>
                            最低：$${data[3].toFixed(4)}<br/>
                            最高：$${data[4].toFixed(4)}<br/>
                            收盘：$${data[2].toFixed(4)}
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
            end: 100,
            minValueSpan: 5
        },
        {
            show: true,
            type: 'slider',
            top: '90%',
            start: 50,
            end: 100,
            minValueSpan: 5
        }
    ],
    series: [
        {
            name: 'Stock Price',
            type: 'candlestick',
            data: [],
            barMinWidth: 1,
            barMaxWidth: 20,
            itemStyle: {
                color: '#06B83F',
                color0: '#E53E3E',
                borderColor: '#06B83F',
                borderColor0: '#E53E3E'
            }
        },
        {
            name: 'Stick',
            type: 'candlestick',
            data: [],
            barMinWidth: 1,
            barMaxWidth: 20,
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
            encode: {
                x: [0],
                y: [1]
            },
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
            encode: {
                x: [0],
                y: [1]
            },
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
            encode: {
                x: [0],
                y: [1]
            },
            connectNulls: true,
            symbol: 'circle',
            symbolSize: 4,
            lineStyle: {
                color: '#4A90E2',
                width: 1
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
            encode: {
                x: [0],
                y: [1]
            },
            connectNulls: true,
            symbol: 'circle',
            symbolSize: 4,
            lineStyle: {
                color: '#FF6B35',
                width: 1
            },
            itemStyle: {
                color: '#FF6B35',
                borderColor: '#E55A2B',
                borderWidth: 1
            }
        },
        {
            name: 'Pivot',
            type: 'custom',
            data: [],
            encode: {
                x: [0, 1],
                y: [2, 3]
            },
            renderItem: function (params, api) {
                const startDate = api.ordinalRawValue(0);
                const endDate = api.ordinalRawValue(1);
                const high = api.value(2);
                const low = api.value(3);

                const startCoord = api.coord([startDate, high]);
                const endCoord = api.coord([endDate, low]);

                return {
                    type: 'rect',
                    shape: {
                        x: startCoord[0],
                        y: endCoord[1],
                        width: endCoord[0] - startCoord[0],
                        height: startCoord[1] - endCoord[1]
                    },
                    style: {
                        fill: 'rgba(138, 138, 135, 0.2)',
                        stroke: '#8A8A87',
                        lineWidth: 1
                    }
                };
            }
        }
    ]
};
myChart.setOption(option);

async function initChart(symbol, interval, newLayers) {
    showLoading();
    chanData = await fetchData(symbol, interval);
    layers = [true, false, false, false, false, false, false, false, false, false];

    myChart = echarts.init(chartDom);

    if (chanData) {
        option.series[0].data = chanData.source.map(item => [item[1], item[2], item[3], item[4]]);
        option.xAxis.data = chanData.source.map(item => item[0]);

        myChart.setOption(option, {
            notMerge: true,
            lazyUpdate: false,
            silent: false
        });
        await updateChart(newLayers);
    } else {
        console.log("No data to update the chart.");
    }
    hideLoading();
}

async function updateChart(newLayers) {
    if (chanData) {
        if (newLayers[1] !== layers[1]) {
            let data = []
            if (newLayers[1]) {
                data = chanData.stick.map(item => [item[1], item[2], item[1], item[2]]);
            }
            myChart.setOption({
                series: [
                    {
                        name: 'Stick',
                        data: data
                    }
                ]
            });
        }
        if (newLayers[2] !== layers[2]) {
            let dataBottom = [], dataTop = [];
            if (newLayers[2]) {
                dataBottom = chanData.fractal.map(item => [item[0], item[1]]);
                dataTop = chanData.fractal.map(item => [item[0], item[2]]);
            }
            myChart.setOption({
                series: [
                    {
                        name: 'Bottom Fractal',
                        data: dataBottom
                    },
                    {
                        name: 'Top Fractal',
                        data: dataTop
                    }
                ]
            });
        }
        if (newLayers[3] !== layers[3]) {
            let data = []
            if (newLayers[3]) {
                data = chanData.stroke.map(item => [item[0], item[1] === '' ? item[2] : item[1]]);
            }
            myChart.setOption({
                series: [
                    {
                        name: 'Stroke',
                        data: data
                    }
                ]
            });
        }
        if (newLayers[4] !== layers[4]) {
            let data = []
            if (newLayers[4]) {
                data = chanData.segment.map(item => [item[0], item[1] === '' ? item[2] : item[1]]);
            }
            myChart.setOption({
                series: [
                    {
                        name: 'Segment',
                        data: data
                    }
                ]
            });
        }
        if (newLayers[5] !== layers[5]) {
            let data = []
            if (newLayers[5]) {
                data = chanData.pivot;
            }
            myChart.setOption({
                series: [
                    {
                        name: 'Pivot',
                        data: data
                    }
                ]
            });
        }
        layers = newLayers;
    } else {
        console.log("No data to update the chart.");
    }
}

window.addEventListener('resize', function () {
    myChart.resize();
});

myChart.on('click', function (params) {
    if (params.componentType === 'series') {
        const dataIndex = params.dataIndex;
        const dates = option.xAxis.data;
        const data = params.data;
        console.log(`Clicked on ${dates[dataIndex]}: 开盘=${data[1]}, 收盘=${data[2]}, 最低=${data[3]}, 最高=${data[4]}`);
    }
});