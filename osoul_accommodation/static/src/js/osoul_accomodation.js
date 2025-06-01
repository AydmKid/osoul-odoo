odoo.define('osoul_accommodation.custom_chart', function (require) {
    var core = require('web.core');
    var Chart = require('chart.min'); // Include Chart.js library

    var CustomChart = core.Class.extend({
        init: function (parent, data) {
            this.data = data;
            this.renderChart();
        },
        renderChart: function () {
            // Code to render a custom chart with tooltips
            // Here you would create a Chart.js pie chart with custom tooltips to display details
        }
    });

    return CustomChart;
});