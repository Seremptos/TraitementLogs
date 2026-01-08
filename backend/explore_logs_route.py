from http import HTTPStatus

import requests
from flask import Response

def explore_logs(path: str) -> Response:
    try:
        search: requests.Response = requests.get(path)
    except requests.exceptions.ConnectionError:
        return Response("Une erreur est survenue", status=HTTPStatus.BAD_GATEWAY)
    except (Exception,):
        return Response("Une erreur est survenue", status=HTTPStatus.INTERNAL_SERVER_ERROR)

    return Response(search.content, status=search.status_code)