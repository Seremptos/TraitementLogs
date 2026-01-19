import hashlib
import json
from http import HTTPStatus
from io import TextIOWrapper

from csv import reader as read_csv
from typing import Final, Collection

import requests
from flask import Response
from requests import post

CHARSET: Final[str] = "utf-8"
MIN_ROW_TO_SEND: Final[int] = 5000

def send_to_database(api_url: str, buffer: list[dict[str, Collection[str]]]) -> int:
    try :
        e: requests.Response = post(api_url, json=json.dumps(buffer, separators=(',', ':')))
        buffer.clear()
        return e.status_code
    except ConnectionError:
        return 500

def process_csv(api_url: str, logfile: TextIOWrapper) -> Response :
    print("Starting csv processing")
    csvreader = read_csv(logfile)
    header: list[str] = next(csvreader)
    buffer: list[dict[str, Collection[str]]] = []
    status_code: int = 0

    for row in csvreader:
        row_joined: str = str.join('', row)
        row_hash: str = hashlib.sha256(row_joined.encode(CHARSET), usedforsecurity=False).hexdigest()
        # Vérifier avec la base de données pour chaque log
        buffer.append(LogLine(row, row_hash).to_dict(header))
        # Envoyer à la BDD
        if len(buffer) >= MIN_ROW_TO_SEND:
            status_code = send_to_database(api_url, buffer)
            if status_code is not 200:
                return Response("An error occured.", status=status_code)

    # Envoyer ce qu'il reste
    if len(buffer) > 0:
        status_code = send_to_database(api_url, buffer)
        if status_code is not 200:
            return Response("An error occured.", status=status_code)
    return Response(status=HTTPStatus.OK)


class LogLine:
    def __init__(self, row: list[str], row_hash: str):
        self.row: list[str] = row
        self.row_hash: str = row_hash

    def to_dict(self, header: list[str]) -> dict[str, Collection[str]]:
        data = {
            "rowHash": self.row_hash,
            "rowContent": dict(zip(header, self.row))
        }
        return data
