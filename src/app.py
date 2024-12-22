from config import Config
from flask import Flask, Response, request
import json
from src.management import VirtNetManagerFactory
from src.policy import PolicyTypes, PolicyFactory


app = Flask(__name__)

(err_manager, manager) = VirtNetManagerFactory.create()
if manager is None:
    raise Exception(err_manager)

@app.route("/virtnet/start", methods=["POST"])
def virtnet_start() -> Response:
    if manager is None:
        return Response(status=500)

    if manager.network_already_up:
        return Response(response="Rede virtual já instanciada.", status=409)

    (err_generation, is_network_up) = manager.virtnet.generate()
    if not is_network_up:
        return Response(response=err_generation, status=500)

    return Response(response="Rede virtual criada com sucesso.", status=201)

@app.route("/virtnet/destroy", methods=["POST"])
def virtnet_destroy() -> Response:
    if manager is None:
        return Response(status=500)

    if not manager.network_already_up:
        return Response(response="Rede virtual não localizada ou offline.",
                        status=500)

    (err_destruction, did_destroy) = manager.virtnet.destroy()
    if not did_destroy:
        return Response(response=err_destruction, status=500)

    return Response(response="Rede virtual destruída com sucesso.",
                    status=status)

@app.route("/virtnet/status")
def virtnet_status() -> Response:
    if manager is None:
        return Response(status=500)

    return Response(response=json.dumps({"status": manager.network_already_up}),
                    status=200)

@app.route("/manager/manage_policy", methods=["POST", "DELETE"])
def manage_policy() -> Response:
    if manager is None:
        return Response(status=500)

    (err_config, config) = Config.get()
    if err_config != "":
        return Response(err_config, status=500)

    try:
        data = request.json
        method = request.method
        
        if method == "POST":
            (err_policy, p) = \
                    PolicyFactory.create_using(policy_data=data,
                                               max_bandwidth=config["max_bandwidth"])
            if p is None:
                return Response(response=err_policy, status=400)

            (err_creation, did_create) = manager.create(policy=p)
            if not did_create:
                return Response(response=err_creation, status=500)

            return Response(response="Política de classificação criada com sucesso!",
                            status=201)
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
                return Response(response="Tipo de tráfego inválido para política de classificação.",
                                status=400)

            (err_remove, did_remove) = \
                    manager.remove_policy_by(traffic_type=traffic_type)
            if not did_remove:
                return Response(response=err_remove, status=500)

            return Response(response="Política de classificação removida com sucesso!",
                            status=status)
        else:
            return Response(response="Método HTTP inválido.", status=405)
    except Exception:
        return Response(status=500)
    
@app.route("/manager/capture_alerts", methods=["POST"])
def capture_alerts() -> Response:
    if manager is None:
        return Response(status=500)

    try:
        alerts_data = request.json
        alerts = alerts_data.get("alerts", None)
        
        (err_alerts, did_process) = manager.process_alerts(alerts)
        if not did_process:
            return Response(response=err_alerts, status=500)

        return Response(response="", status=200)

    except Exception as e:
        return Response(response=f"Falha ao recuperar informações de alertas: {repr(e)}",
                        status=400)

@app.route("/status")
def status() -> Response:
    return Response(status=200)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

