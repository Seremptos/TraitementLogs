from typing import Final

from flask import Flask, Response

from explore_logs_route import explore_logs
from process_logs_route import process_logs

app = Flask("TraitementLogs")

DATABASE_API_URL: Final[str] = "http://bdd_api:6000"
SEND_LOGS_URL: Final[str] = DATABASE_API_URL+"/logsreceive"
SEARCH_LOGS_URL: Final[str] = DATABASE_API_URL+"/search/"

@app.route("/process", methods=["POST"])
def process_logs_route() -> Response:
    return process_logs(SEND_LOGS_URL)

@app.route("/search/<path:search_path>", methods=["GET"])
def explore_logs_route(search_path) -> Response:
    return explore_logs(SEARCH_LOGS_URL + search_path)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)