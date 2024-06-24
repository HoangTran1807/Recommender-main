from flask import Blueprint, request
from utils.content_base import renderContent, get_trainData, createModel, recommendProduct, recommendProducts
import time as Time
from flask import jsonify

ContentBase = Blueprint('ContentBase', __name__)


@ContentBase.route('/', methods=['GET'])
def index():
    return 'ContentBase index'

@ContentBase.route('/content', methods=['GET'])
def content():
    return renderContent()

@ContentBase.route('/createTrainingData', methods=['GET'])
def createTrainingData():
    print("Start train Content based")
    get_trainData()
    return createModel()

@ContentBase.route('/createModel', methods=['GET'])
def createModelRoute():
    return createModel()

@ContentBase.route('/recommendProduct/<product_id>', methods=['GET'])
def recommendProductRoute(product_id):
    take = int(request.args.get("take", -1))
    rs = recommendProduct(product_id, 10)
    print(rs)
    return (
        jsonify({"userId": 0, "take": take, "time": rs['time'], "list": rs['data']}),
        200,
    )


@ContentBase.route("/recommendProducts", methods=["GET"])
def recommendProductsRoute():
    data = request.args.get("ids", "")
    list_product_id = [int(x) for x in data.split(",")]
    take = int(request.args.get("take", -1))
    return recommendProducts(list_product_id, take)
