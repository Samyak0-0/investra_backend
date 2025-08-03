from flask import Blueprint, request, jsonify
from lstm.predictions import predict

predictions_bp = Blueprint("predictions", __name__)

@predictions_bp.route("/predict/<symbol>", methods=["GET"])
def predict_stock(symbol):
    try:
        days = int(request.args.get("days", 30))  # default 30 days

        # Call your LSTM model prediction function
        # predicted_prices = predict(days, symbol.upper())

        # # Convert np.ndarray → list for JSON
        # prediction_list = predicted_prices.flatten().tolist()
        predictions = predict(days, symbol)
        return predictions 

    except Exception as e:
        return jsonify({"error": str(e)}), 500
