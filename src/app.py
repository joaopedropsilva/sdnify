from flask import Flask, Response, request

from src.management import Managers
from src.data import Warning, Error

app = Flask(__name__)
managers = Managers()

@app.route("/start", method="POST")
def start() -> Response:
    if managers.is_network_alive:
        return Response(response=Warning.NetworkAlreadyUp, status=409)

    generation_result = managers.virtual_network.generate()

    status = 201
    if isinstance(generation_result, Error):
        status = 500

    return Response(response=generation_result, status=status)

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

@app.route("/manage_policy", methods=["POST", "PUT", "DELETE"])
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
        elif method == "PUT":
            update_result = managers.flow.update(policy)
        elif method == "DELETE":
            removal_result = managers.flow.remove(policy)
        else:
            return Response(response="Método HTTP inválido.", status=405)
    except Exception:
        return Response(status=500)
    
@app.route("/capture_alerts")
def capture_alerts(policy_data: dict) -> Response:
    return "ok"

if __name__ == "__main__":
    app.run()

