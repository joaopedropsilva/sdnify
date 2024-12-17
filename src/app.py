from flask import Flask, Response, request
import json

from src.management import VirtNetManager
from src.data import Success, Warning, Error
from src.policy import PolicyTypes, PolicyFactory
from src.utils import File


app = Flask(__name__)
manager = VirtNetManager()

@app.route("/virtnet/start", methods=["POST"])
def virtnet_start() -> Response:
    if manager.network_already_up:
        return Response(response="Rede virtual já instanciada.", status=409)

    (err, is_network_up) = manager.virtnet.generate()

    if not is_network_up:
        return Response(response=err, status=500)

    return Response(response="Rede virtual criada com sucesso.", status=201)

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

@app.route("/manager/manage_policy", methods=["POST", "DELETE"])
def manage_policy() -> Response:
    try:
        data = request.json
        method = request.method
        

        status = 400
        if method == "POST":
            factory = \
                PolicyFactory(policy_data=data,
                              max_bandwidth=File.get_config()["max_bandwidth"])

            (create_type_result, p) = factory.create()

            if isinstance(create_type_result, Error):
                return Response(response=create_type_result.value,
                                status=status)

            if p is None:
                return Response(status=500)

            creation_result = manager.flow.create(policy=p)

            if isinstance(creation_result, Success):
                status = 201

            return Response(response=creation_result.value, status=status)
        elif method == "DELETE":
            traffic_type = str()
            try:
                traffic_type = data["traffic_type"]
            except KeyError:
                return Response(response="Atributo traffic_type ausente.",
                                status=400)
            try:
                traffic_type = PolicyTypes[traffic_type.upper()]
            except KeyError:
                return Response(response=Error.InvalidPolicyTrafficType.value,
                                status=400)

            removal_result = \
                    manager.flow.remove_policy_by(traffic_type=traffic_type)

            if isinstance(removal_result, Success):
                status = 200

            return Response(response=removal_result.value, status=status)
        else:
            return Response(response="Método HTTP inválido.", status=405)
    except Exception:
        return Response(status=500)
    
@app.route("/manager/capture_alerts", methods=["POST"])
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

