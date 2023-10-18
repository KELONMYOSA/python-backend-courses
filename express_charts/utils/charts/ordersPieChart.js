const ChartJsImage = require('chartjs-to-image');

async function generateOrdersPieChart(email, orders) {
    let dishCount = {};
    for (let order = 0; order < orders.length; order++) {
        for (let position = 0; position < orders[order].length; position++) {
            const dishName = orders[order][position].menu_position.name;
            const count = orders[order][position].count;
            dishCount[dishName] = (dishCount[dishName] || 0) + count;
        }
    }

    const chart = new ChartJsImage();
    chart.setConfig({
        type: 'pie',
        data: {
            labels: Object.keys(dishCount),
            datasets: [
                {
                    label: email,
                    data: Object.keys(dishCount).map(function (key) {
                        return dishCount[key];
                    })
                }
            ]
        }
    });

    return await chart.toBinary();
}

exports.generateOrdersPieChart = generateOrdersPieChart;
