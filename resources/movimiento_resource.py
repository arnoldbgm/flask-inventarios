from datetime import datetime, timezone

from flask import request
from flask_restful import Resource
from flasgger import swag_from

from db import db
from models.movimiento import MovimientoStock
from models.producto import Producto


class MovimientoListResource(Resource):
    @swag_from({
        "tags": ["Movimientos de Stock"],
        "summary": "Listar todos los movimientos de stock",
        "responses": {
            200: {
                "description": "Lista de movimientos",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "producto_id": {"type": "integer"},
                            "tipo": {"type": "string"},
                            "cantidad": {"type": "integer"},
                            "fecha": {"type": "string"},
                            "motivo": {"type": "string"},
                            "producto_nombre": {"type": "string"},
                        },
                    },
                },
            }
        },
    })
    def get(self):
        movimientos = MovimientoStock.query.order_by(MovimientoStock.fecha.desc()).all()
        result = []
        for m in movimientos:
            item = m.to_dict()
            item["producto_nombre"] = m.producto.nombre if m.producto else None
            result.append(item)
        return result

    @swag_from({
        "tags": ["Movimientos de Stock"],
        "summary": "Registrar un movimiento de stock (entrada/salida)",
        "description": (
            "Si el tipo es 'salida', valida que haya stock suficiente "
            "antes de registrar. Luego actualiza el stock del producto automáticamente."
        ),
        "parameters": [
            {
                "in": "body",
                "name": "movimiento",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "producto_id": {"type": "integer", "example": 1},
                        "tipo": {
                            "type": "string",
                            "enum": ["entrada", "salida"],
                            "example": "entrada",
                        },
                        "cantidad": {"type": "integer", "example": 50},
                        "motivo": {
                            "type": "string",
                            "example": "Reposición de inventario",
                        },
                    },
                },
            }
        ],
        "responses": {
            201: {"description": "Movimiento registrado y stock actualizado"},
            400: {"description": "Datos inválidos o stock insuficiente"},
            404: {"description": "Producto no encontrado"},
        },
    })
    def post(self):
        data = request.get_json()

        if not data or not data.get("producto_id"):
            return {"message": "El producto es obligatorio"}, 400

        if not data.get("tipo") or data["tipo"] not in ("entrada", "salida"):
            return {"message": "El tipo debe ser 'entrada' o 'salida'"}, 400

        if not data.get("cantidad") or int(data["cantidad"]) <= 0:
            return {"message": "La cantidad debe ser un número positivo"}, 400

        producto = Producto.query.get(data["producto_id"])
        if not producto:
            return {"message": "Producto no encontrado"}, 404

        cantidad = int(data["cantidad"])
        tipo = data["tipo"]

        if tipo == "salida" and producto.stock < cantidad:
            return {
                "message": f"Stock insuficiente. Stock actual: {producto.stock}, solicitado: {cantidad}"
            }, 400

        if tipo == "entrada":
            producto.stock += cantidad
        else:
            producto.stock -= cantidad

        movimiento = MovimientoStock(
            producto_id=int(data["producto_id"]),
            tipo=tipo,
            cantidad=cantidad,
            fecha=datetime.now(timezone.utc),
            motivo=data.get("motivo", ""),
        )
        db.session.add(movimiento)
        db.session.commit()

        item = movimiento.to_dict()
        item["producto_nombre"] = producto.nombre
        item["stock_actual"] = producto.stock
        return item, 201


class MovimientoResource(Resource):
    @swag_from({
        "tags": ["Movimientos de Stock"],
        "summary": "Obtener un movimiento por ID",
        "parameters": [
            {"in": "path", "name": "id", "type": "integer", "required": True},
        ],
        "responses": {
            200: {"description": "Movimiento encontrado"},
            404: {"description": "Movimiento no encontrado"},
        },
    })
    def get(self, id):
        movimiento = MovimientoStock.query.get(id)

        if not movimiento:
            return {"message": "Movimiento no encontrado"}, 404

        item = movimiento.to_dict()
        item["producto_nombre"] = movimiento.producto.nombre if movimiento.producto else None
        return item
