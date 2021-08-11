from requests import post as rpost, get as rget, Response
from flask import request
from const import DGAPI_SERVER


class DGAPI:

    @classmethod
    def get(endpoint: str, headers: dict = None) -> Response:
        """
        Realiza una peticion get al dg suite
        """
        nheaders = {**request.headers}
        headers and nheaders.update(**headers)
        return rget(DGAPI_SERVER + endpoint, headers=nheaders)

    @classmethod
    def post(endpoint: str, body: dict, headers: dict = None):
        """
        Realiza una peticion post al dg suite
        """
        nheaders = {**request.headers}
        headers and nheaders.update(**headers)
        return rpost(DGAPI_SERVER + endpoint, json=body, headers=nheaders)
