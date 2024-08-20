
"use strict";

var KTWidgets = {
    init: function () {
        this.initCharts();
    },

    initCharts: function () {
        var $charts = $(".mixed-widget-7-chart");
        $charts.each(function () {
            var $chart = $(this);
            var height = parseInt($chart.css("height"));
            var color = $chart.data("kt-chart-color");
            var gray800 = KTUtil.getCssVariableValue("--bs-gray-800");
            var gray300 = KTUtil.getCssVariableValue("--bs-gray-300");
            var chartColor = KTUtil.getCssVariableValue("--bs-" + color);
            var lightColor = KTUtil.getCssVariableValue("--bs-light-" + color);

            $.ajax({
                url: url_transfer_month, // Cambia esto a la URL correcta de tu vista
                method: 'GET',
                success: function (data) {
                    var categories = Object.keys(data);
                    var seriesData = Object.values(data);

                    KTWidgets.renderChart($chart, height, chartColor, lightColor, gray800, gray300, categories, seriesData, 'Traslados por mes');
                }
            });
        });
    },

    renderChart: function ($chart, height, chartColor, lightColor, gray800, gray300, categories, seriesData, name) {
        new ApexCharts($chart[0], {
            series: [{
                name: name,
                data: seriesData,
            }],
            chart: {
                fontFamily: "inherit",
                type: "area",
                height: height,
                toolbar: { show: false },
                zoom: { enabled: false },
                sparkline: { enabled: true },
            },
            plotOptions: {},
            legend: { show: false },
            dataLabels: { enabled: false },
            fill: { type: "solid", opacity: 1 },
            stroke: {
                curve: "smooth",
                show: true,
                width: 3,
                colors: [chartColor],
            },
            xaxis: {
                categories: categories,
                axisBorder: { show: false },
                axisTicks: { show: false },
                labels: {
                    show: false,
                    style: { colors: gray800, fontSize: "12px" },
                },
                crosshairs: {
                    show: false,
                    position: "front",
                    stroke: {
                        color: gray300,
                        width: 1,
                        dashArray: 3,
                    },
                },
                tooltip: {
                    enabled: true,
                    formatter: undefined,
                    offsetY: 0,
                    style: { fontSize: "12px" },
                },
            },
            yaxis: {
                min: 0,
                max: Math.max(...seriesData) + 10,
                labels: {
                    show: false,
                    style: { colors: gray800, fontSize: "12px" },
                },
            },
            states: {
                normal: { filter: { type: "none", value: 0 } },
                hover: { filter: { type: "none", value: 0 } },
                active: {
                    allowMultipleDataPointsSelection: false,
                    filter: { type: "none", value: 0 },
                },
            },
            tooltip: {
                style: { fontSize: "12px" },
                y: {
                    formatter: function (val) {
                        return val + " Traslados";
                    },
                },
            },
            colors: [lightColor],
            markers: {
                colors: [lightColor],
                strokeColor: [chartColor],
                strokeWidth: 3,
            },
        }).render();
    }
};

$(document).ready(function () {
    KTWidgets.init();
});
