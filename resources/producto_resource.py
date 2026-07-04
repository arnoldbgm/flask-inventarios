from flask import request
from flask_restful import Resource
from flasgger import swag_from

from db import db
from models.producto import Producto
from models.categoria import Categoria


class ProductoListResource(Resource):
    @swag_from({
        "tags": ["Productos"],
        "summary": "Listar todos los productos",
        "parameters": [
            {
                "in": "query",
                "name": "stock_min",
                "type": "integer",
                "required": False,
                "description": "Filtrar por stock mínimo",
            },
            {
                "in": "query",
                "name": "categoria_id",
                "type": "integer",
                "required": False,
                "description": "Filtrar por categoría",
            },
        ],
        "responses": {
            200: {
                "description": "Lista de productos",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "nombre": {"type": "string"},
                            "precio": {"type": "number"},
                            "stock": {"type": "integer"},
                            "categoria_id": {"type": "integer"},
                            "categoria_nombre": {"type": "string"},
                        },
                    },
                },
            }
        },
    })
    def get(self):
        query = Producto.query

        stock_min = request.args.get("stock_min", type=int)
        if stock_min is not None:
            query = query.filter(Producto.stock >= stock_min)

        categoria_id = request.args.get("categoria_id", type=int)
        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)

        productos = query.all()
        result = []
        for p in productos:
            item = p.to_dict()
            item["categoria_nombre"] = p.categoria.nombre if p.categoria else None
            result.append(item)

        return result

    @swag_from({
        "tags": ["Productos"],
        "summary": "Crear un producto",
        "parameters": [
            {
                "in": "body",
                "name": "producto",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "nombre": {"type": "string", "example": "Leche Entera"},
                        "precio": {"type": "number", "example": 4.50},
                        "stock": {"type": "integer", "example": 100},
                        "categoria_id": {"type": "integer", "example": 1},
                    },
                },
            }
        ],
        "responses": {
            201: {"description": "Producto creado"},
            400: {"description": "Datos inválidos o categoría no existe"},
        },
    })
    def post(self):
        data = request.get_json()

        if not data or not data.get("nombre"):
            return {"message": "El nombre es obligatorio"}, 400

        if not data.get("precio"):
            return {"message": "El precio es obligatorio"}, 400

        if not data.get("categoria_id"):
            return {"message": "La categoría es obligatoria"}, 400

        categoria = Categoria.query.get(data["categoria_id"])
        if not categoria:
            return {"message": "La categoría no existe"}, 400

        producto = Producto(
            nombre=data["nombre"],
            precio=float(data["precio"]),
            stock=int(data.get("stock", 0)),
            categoria_id=int(data["categoria_id"]),
        )
        db.session.add(producto)
        db.session.commit()

        item = producto.to_dict()
        item["categoria_nombre"] = producto.categoria.nombre
        return item, 201


class ProductoResource(Resource):
    @swag_from({
        "tags": ["Productos"],
        "summary": "Obtener un producto por ID",
        "parameters": [
            {"in": "path", "name": "id", "type": "integer", "required": True},
        ],
        "responses": {
            200: {"description": "Producto encontrado"},
            404: {"description": "Producto no encontrado"},
        },
    })
    def get(self, id):
        producto = Producto.query.get(id)

        if not producto:
            return {"message": "Producto no encontrado"}, 404

        item = producto.to_dict()
        item["categoria_nombre"] = producto.categoria.nombre if producto.categoria else None
        return item

    @swag_from({
        "tags": ["Productos"],
        "summary": "Actualizar un producto",
        "parameters": [
            {"in": "path", "name": "id", "type": "integer", "required": True},
            {
                "in": "body",
                "name": "producto",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "nombre": {"type": "string"},
                        "precio": {"type": "number"},
                        "stock": {"type": "integer"},
                        "categoria_id": {"type": "integer"},
                    },
                },
            },
        ],
        "responses": {
            200: {"description": "Producto actualizado"},
            404: {"description": "Producto no encontrado"},
        },
    })
    def put(self, id):
        data = request.get_json()
        producto = Producto.query.get(id)

        if not producto:
            return {"message": "Producto no encontrado"}, 404

        if "categoria_id" in data:
            categoria = Categoria.query.get(data["categoria_id"])
            if not categoria:
                return {"message": "La categoría no existe"}, 400
            producto.categoria_id = int(data["categoria_id"])

        producto.nombre = data.get("nombre", producto.nombre)
        producto.precio = float(data.get("precio", producto.precio))
        producto.stock = int(data.get("stock", producto.stock))
        db.session.commit()

        item = producto.to_dict()
        item["categoria_nombre"] = producto.categoria.nombre if producto.categoria else None
        return item

    @swag_from({
        "tags": ["Productos"],
        "summary": "Eliminar un producto",
        "parameters": [
            {"in": "path", "name": "id", "type": "integer", "required": True},
        ],
        "responses": {
            200: {"description": "Producto eliminado"},
            404: {"description": "Producto no encontrado"},
        },
    })
    def delete(self, id):
        producto = Producto.query.get(id)

        if not producto:
            return {"message": "Producto no encontrado"}, 404

        db.session.delete(producto)
        db.session.commit()

        return {"message": "Producto eliminado"}
