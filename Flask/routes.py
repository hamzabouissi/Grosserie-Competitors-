from flask import Flask
import mongoengine as me
from .Documents import Products

app = Flask(__name__)

me.connect(
    db='Crawler',
    username='root',
    password='root',
    authentication_source="admin"
)




@app.route('/Product/<string:barcode>')
def get_product(barcode):
    
    product = Products.objects(barcode=barcode).to_json()
    return product


@app.route('/Product/<string:barcode>/History')
def product_history(barcode):
    
    products = Products.aggregate([
            {
                "$lookup":
                {
                    "from": "PriceLogs",
                    "pipeline": [
                        { "$match":
                            {"product_barcode":barcode}
                        },
                    ],
                    "as": "product_prices"
                }
            }
        ])
    return products




