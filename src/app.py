from flask import Flask, Response, request
import json

from src.management import VirtNetManager
from src.data import Warning, Error

app = Flask(__name__)
manager = VirtNetManager()

@app.route("/virtnet/start", methods=["POST"])
def virtnet_start() -> Response:
    if manager.network_already_up:
        return Response(response=Warning.NetworkAlreadyUp, status=409)

    generation_result = manager.virtnet.generate()

    status = 201
    if isinstance(generation_result, Error):
        status = 500

    return Response(response=generation_result.value, status=status)

@app.route("/virtnet/destroy", methods=["POST"])
def virtnet_destroy() -> Response:
    if not manager.network_already_up:
        return Response(response=Warning.NetworkUnreachable, status=500)

    destruction_result = manager.virtnet.destroy()

    status = 200
    if isinstance(destruction_result, Error):
        status=500

    return Response(response=destruction_result.value, status=status)

@app.route("/virtnet/status")
def virtnet_status() -> Response:
    return Response(response=json.dumps({"status": manager.network_already_up}),
                    status=200)

@app.route("/controller/manage_policy", methods=["POST", "DELETE"])
def manage_policy() -> Response:
    try:
        policy = request.json
        method = request.method
        
        if method == "POST":
            creation_result = manager.flow.create(policy)

            status = 201
            if isinstance(creation_result, Error):
                status = 400

            return Response(response=creation_result.value, status=status)
        elif method == "DELETE":
            removal_result = manager.flow.remove(policy)

            status = 200
            if isinstance(removal_result, Error):
                status = 400

            return Response(response=removal_result.value, status=status)
        else:
            return Response(response="Método HTTP inválido.", status=405)
    except Exception:
        return Response(status=500)
    
@app.route("/controller/capture_alerts", methods=["POST"])
def capture_alerts() -> Response:
    try:
        alerts_data = request.json
        alerts = alerts_data.get("alerts", None)
        
        result = manager.flow.process_alerts(alerts)

        if isinstance(result, Error): 
            return Response(
                response=json.dumps({"error": "Internal server error"}),
                status=500,
                mimetype="application/json",
            )
        
        return Response(
                response=json.dumps({"message": "Alertas processados com sucesso."}),
                status=200,
                mimetype="application/json",
            )

    except Exception as e:
        return Response(
            response=json.dumps({"error": "Internal server error", "details": str(e)}),
            status=500,
            mimetype="application/json",
        )

@app.route("/status")
def status() -> Response:
    return Response(status=200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

