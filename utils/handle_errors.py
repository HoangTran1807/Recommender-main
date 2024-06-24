from functools import wraps
from flask import jsonify

def with_error_handling():
    def decorator(callable):

        @wraps(callable)
        def wrapper(*args, **kwargs):
            try:
                return callable(*args, **kwargs)
            except Exception as e:
                error_message = str(e)
                print(error_message, "rrrr")
                return jsonify({"error": error_message}), 500

        return wrapper

    return decorator
