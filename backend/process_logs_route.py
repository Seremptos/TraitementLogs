import io
import os
from http import HTTPStatus
from typing import Final

import requests.exceptions
from flask import Response, request
from werkzeug.datastructures import FileStorage

from process_csv import process_csv

UPLOADS_PATH: Final[str] = "uploads/"

# Créer le fichier si n'existe pas
if not os.path.exists(UPLOADS_PATH):
    os.makedirs(UPLOADS_PATH, exist_ok=True)

#
for file in os.listdir(UPLOADS_PATH):
    os.remove(os.path.join(UPLOADS_PATH, file))

def process_logs(api_url: str) -> Response:
    missing_file: Response = Response("Missing file.", status=HTTPStatus.BAD_REQUEST)

    # Si le fichier n'est pas présent
    if 'file' not in request.files:
        return missing_file

    uploaded_file: FileStorage = request.files['file']

    if uploaded_file.filename != "":
        try:
            return process_csv(api_url, io.TextIOWrapper(uploaded_file.stream, encoding='utf-8-sig'))
        except ValueError:
            return Response("Bad file.", status=HTTPStatus.BAD_REQUEST)
        except requests.exceptions.ConnectionError:
            return Response("An error occured.", status=HTTPStatus.BAD_GATEWAY)
        except Exception as e:
            print(str(e))
            return Response("An error occured.", status=HTTPStatus.INTERNAL_SERVER_ERROR)

    return missing_file
