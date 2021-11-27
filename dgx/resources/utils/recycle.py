from collections import defaultdict
from bson import ObjectId
from datetime import datetime
from flask import session
from mongoCon import MongoCon
from pymongo import InsertOne, database


class Recycle:
    """
    Funciones para el manejo de la papelera
    """

    def __init__(self, cnx: (dict or database.Database) = None):
        self.__cnx = cnx

    @staticmethod
    def add_event(item: dict, event: str):
        user = session.get('user_name', 'System')
        events = item.get("events", [])
        events.append({
            "event": event,
            "user": user,
            "datetime": datetime.now(),
            "msg": "The user {} has {} this registry.".format(user, event)
        })
        item.update({"events": events})

    @classmethod
    def __add(self, cnx: database.Database, collection: str, query: dict, display: str):
        opts = []
        _ids = []
        nw = datetime.now()
        for item in cnx[collection].find(query):
            self.add_event(item, "deleted")
            opts.append(
                InsertOne({
                    "group_code": item['group_code'],
                    "dealer_code": item['dealer_code'],
                    "type": collection,
                    "delete_date": nw,
                    "deleted_by": session.get('user_name', 'System'),
                    "display": display.format(**item),
                    "item": item
                })
            )
            _ids.append(item["_id"])  # agrega identificador a eliminar
        if opts:
            cnx[collection].bulk_write(opts)
            cnx[collection].delete_many({"_id": {"$in": _ids}})

    @classmethod
    def __recovery(self, cnx: database.Database, _ids: list):
        query = {"_id": {"$in": _ids}}
        items = list(cnx.recycle.find(query))
        tpsC = defaultdict(list)  # tipos de collecion
        if items:
            for item in items:
                self.add_event(item['item'], "restored")
                item["item"].pop("_id")
                tpsC[item['type']].append(item['item'])  # agrega el tipo
            for cname, citems in tpsC.items():
                cnx[cname].insert_many(citems)
            cnx.recycle.delete_many(query)

    @classmethod
    def add(self, collection: str, query: dict, display: str):
        tpe = type(self.__cnx)  # tipo de coneccion
        if tpe is dict:
            with MongoCon() as cnx:
                self.__add(cnx, collection, query, display)
        elif tpe is database.Database:
            self.__add(self.__cnx, collection, query, display)

    @classmethod
    def recovery(self, _ids: (list or str or ObjectId)):
        """
        Recupera los items borrados
        """
        tpe = type(_ids)
        # evalua el tipo de dato
        if tpe in (list, tuple):
            aux = []
            for _id in _ids:
                itpe = type(_id)
                if itpe is str:
                    aux.append(ObjectId(_id))
                elif itpe is ObjectId:
                    aux.append(_id)
                else:
                    raise Exception("Object '%s' kind of %s is not supported" % (_id, itpe))
            _ids = aux
        elif tpe is str:
            _ids = (ObjectId(_ids), )
        elif tpe is not ObjectId:
            raise Exception("Object '%s' kind of %s is not supported" % (_ids, tpe))
        if _ids:
            tpe = type(self.__cnx)  # tipo de coneccion
            if tpe is dict:
                with MongoCon() as cnx:
                    self.__recovery(cnx, _ids)
            elif tpe is database.Database:
                self.__recovery(self.__cnx, _ids)
