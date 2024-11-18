from flask import Flask, Response, jsonify, request

from management import Managers
from data import Warning, Error

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
        policy_data = request.json
        method = request.method
        
        if method == "POST":
            result = managers.flow.create(policy_data)
        elif method == "PUT":
            result = managers.flow.update(policy_data)
        elif method == "DELETE":
            result = managers.flow.remove(policy_data)
        
        else:
            return jsonify({"error": "Método HTTP Inválido."}), 405
    
        if result.status:
            return jsonify({"status": "success", "payload": result.payload}), 200
        
        if result.status:
            return jsonify({"status": "failure", "payload": result.err_reason}), 400

    except KeyError as e:
        return jsonify({"error": "Dados Inválidos ou Incompletos.", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Erro no Servidor.", "details": str(e)}), 500
    
@app.route("/capture_alerts")
def capture_alerts(policy_data: dict) -> Response:
    return "ok"

if __name__ == "__main__":
    app.run()
