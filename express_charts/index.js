const express = require('express');
const bodyParser = require('body-parser');
const handleErrors = require('./middleware/handleErrors');
const { BadRequest } = require('./utils/errors');
const {generateOrdersPieChart} = require("./utils/charts/ordersPieChart");

const PORT = process.env.PORT || 3000;
const app = express();

app.use(bodyParser.json());

app.post('/chart/dishes', async (req, res, next) => {
    const {email, orders} = req.body;

    try {
        if (!email || !orders) {
            throw new BadRequest('Missing required fields: email or orders');
        }
        const img_binary = await generateOrdersPieChart(email, orders);
        res.contentType('image/png');
        res.end(img_binary, 'binary');
    } catch (err) {
        next(err)
    }
});

app.use(handleErrors);

app.listen(PORT, () => {
    console.log(`Server listening on ${PORT}`);
});
