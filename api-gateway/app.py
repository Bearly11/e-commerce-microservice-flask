from flask import Flask, request, Response
import requests

app = Flask(__name__)

SERVICES = {
    "products": "http://product-service:5000",
    "orders": "http://order-service:5001",
    "users": "http://user-service:5002",
}


@app.route("/<service>", methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/<service>/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def gateway(service, path=""):
    if service not in SERVICES:
        return {"error": "Service not found"}, 404

    service_url = SERVICES[service]
    if path:
        url = f"{service_url}/{service}/{path}"
    else:
        url = f"{service_url}/{service}"

    response = requests.request(
        method=request.method,
        url=url,
        json=request.get_json(silent=True),
        params=request.args
    )

    return Response(response.content, status=response.status_code)


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080)