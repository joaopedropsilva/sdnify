from flask import Flask, Response, jsonify, request

app = Flask(__name__)

# Remover dependências antigas das classes

@app.route("/start", method="POST")
def start(self) -> Response:
    if not self.__topo_manager.generate():
        return Response(
            response="Não foi possível iniciar a rede",
            status=500
        )

    return Response(
        response="Rede iniciada com sucesso",
        status=201
    )


@app.route("/destroy")
def destroy(self) -> Response:
    self.__topo_manager.destroy()

@app.route("/get_statistics")
def get_statistics(self) -> Response:
    return "ok"

@app.route("/manage_policy", methods=["POST", "PUT", "DELETE"])
def manage_policy(self) -> Response:
    try:
        policy_data = request.json
        method = request.method
        
        if method == "POST":
            result = self.__flow_manager.create(policy_data)
        elif method == "PUT":
            result = self.__flow_manager.update(policy_data)
        elif method == "DELETE":
            result = self.__flow_manager.remove(policy_data)
        
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
def capture_alerts(self, policy_data: dict) -> Response:
    return "ok"

app.run()

