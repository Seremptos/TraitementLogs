import hashlib
import json
from http import HTTPStatus

import flask
import os
from csv import reader as read_csv
from typing import Final, Collection

import requests
from flask import Response
from requests import post

CHARSET: Final[str] = "utf-8"
MIN_ROW_TO_SEND: Final[int] = 5000

def send_to_database(api_url: str, buffer: list[dict[str, Collection[str]]]) -> bool:
    try :
        e: requests.Response = post(api_url, json=json.dumps(buffer, separators=(',', ':')))
        if e.status_code != 200:
            # Bof on renvoie pas le bon code mais bon ok
            return False
    except ConnectionError:
        return False
    buffer.clear()
    return True



def process_csv(api_url: str, filepath: str) -> Response :
    with open(filepath, encoding="utf-8-sig") as logfile:
        csvreader = read_csv(logfile)
        header: list[str] = next(csvreader)
        buffer: list[dict[str, Collection[str]]] = []

        for row in csvreader:
            row_joined: str = str.join('', row)
            row_hash: str = hashlib.sha256(row_joined.encode(CHARSET), usedforsecurity=False).hexdigest()
            # Vérifier avec la base de données pour chaque log
            buffer.append(LogLine(row, row_hash).to_dict(header))
            # Envoyer à la BDD
            if len(buffer) >= MIN_ROW_TO_SEND:
                if not send_to_database(api_url, buffer):
                    os.remove(filepath)
                    return Response("An error occured.", status=HTTPStatus.BAD_GATEWAY)
        # Envoyer ce qu'il reste
        if len(buffer) > 0:
            if not send_to_database(api_url, buffer):
                os.remove(filepath)
                return Response("An error occured.", status=HTTPStatus.BAD_GATEWAY)
    os.remove(filepath)
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