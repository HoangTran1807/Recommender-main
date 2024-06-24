import os
from flask import Blueprint, request, jsonify
from utils.collaborative import CollaborativeRecommenderStore
from utils.handle_errors import with_error_handling
import time as Time

collab_blueprint = Blueprint(
    "collab",
    __name__,
    url_prefix="/collab",
)


@collab_blueprint.route("/product", methods=["GET"])
@with_error_handling()
def recommend_product():
    start_time = Time.time()

    userId = int(request.args.get("userId", 0))
    take = int(request.args.get("take", -1))
    recommender = CollaborativeRecommenderStore.get_instance()
    list = recommender.get_suggestions(userId, take)

    people_dicts = [p.product_id for p in list]

    end_time = Time.time()
    time = end_time - start_time
    print("Time: ", time, "take: ", take, 'list: ', people_dicts)
    return (
        jsonify({"userId": userId, "take": take, "time": time, "list": people_dicts}),
        200,
    )


@collab_blueprint.route("/train", methods=["GET"])
@with_error_handling()
def train_recommend():
    print("Start train CollabFilter")
    start_time = Time.time()

    if os.path.exists(CollaborativeRecommenderStore.saved_model):
        # Xóa tệp
        os.remove(CollaborativeRecommenderStore.saved_model)
        CollaborativeRecommenderStore.recommender = None
        recommender = CollaborativeRecommenderStore.get_instance()
    else:
        CollaborativeRecommenderStore.recommender = None
        recommender = CollaborativeRecommenderStore.get_instance()

    end_time = Time.time()
    time = end_time - start_time
    return (
        jsonify(
            {
                "success": True,
                "message": "Train successfully",
                "time": time,
            }
        ),
        200,
    )
