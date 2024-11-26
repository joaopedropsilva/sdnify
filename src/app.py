from flask import Flask, Response, request
import json

from src.management import Managers
from src.data import Warning, Error

app = Flask(__name__)
managers = Managers()

@app.route("/start", methods=["POST"])
def start() -> Response:
    if managers.is_network_alive:
        return Response(response=Warning.NetworkAlreadyUp, status=409)

    generation_result = managers.virtual_network.generate()

    status = 201
    if isinstance(generation_result, Error):
        status = 500

    return Response(response=generation_result.value, status=status)

@app.route("/destroy")
def destroy() -> Response:
    if not managers.is_network_alive:
        return Response(response=Warning.NetworkUnreachable, status=500)

    destruction_result = managers.virtual_network.destroy()

    status = 200
    if isinstance(destruction_result, Error):
        status=500

    return Response(response=destruction_result, status=status)

@app.route("/get_statistics")
def get_statistics() -> Response:
    return "ok"

@app.route("/manage_policy", methods=["POST", "DELETE"])
def manage_policy() -> Response:
    try:
        policy = request.json
        method = request.method
        
        if method == "POST":
            creation_result = managers.flow.create(policy)

            status = 201
            if isinstance(creation_result, Error):
                status = 400

            return Response(response=creation_result, status=status)
        elif method == "DELETE":
            removal_result = managers.flow.remove(policy)

            status = 200
            if isinstance(removal_result, Error):
                status = 400

            return Response(response=removal_result, status=status)
        else:
            return Response(response="Método HTTP inválido.", status=405)
    except Exception:
        return Response(status=500)
    
@app.route("/capture_alerts", methods=["POST"])
def capture_alerts() -> Response:
    try:
        alerts_data = request.json
        alerts = alerts_data.get("alerts", None)
        
        result = managers.flow.process_alerts(alerts)

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

if __name__ == "__main__":
    app.run(host:="0.0.0.0", port=5000)

