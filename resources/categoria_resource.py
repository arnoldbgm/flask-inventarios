from flask import request
from flask_restful import Resource
from flasgger import swag_from

from db import db
from models.categoria import Categoria
from models.producto import Producto


class CategoriaListResource(Resource):
    @swag_from({
        "tags": ["Categorías"],
        "summary": "Listar todas las categorías",
        "responses": {
            200: {
                "description": "Lista de categorías",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "nombre": {"type": "string"},
                            "descripcion": {"type": "string"},
                        },
                    },
                },
            }
        },
    })
    def get(self):
        categorias = Categoria.query.all()
        return [c.to_dict() for c in categorias]

    @swag_from({
        "tags": ["Categorías"],
        "summary": "Crear una categoría",
        "parameters": [
            {
                "in": "body",
                "name": "categoria",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "nombre": {"type": "string", "example": "Lácteos"},
                        "descripcion": {"type": "string", "example": "Productos derivados de la leche"},
                    },
                },
            }
        ],
        "responses": {
            201: {"description": "Categoría creada"},
            400: {"description": "Falta el nombre"},
        },
    })
    def post(self):
        data = request.get_json()

        if not data or not data.get("nombre"):
            return {"message": "El nombre es obligatorio"}, 400

        categoria = Categoria(
            nombre=data["nombre"],
            descripcion=data.get("descripcion", ""),
        )
        db.session.add(categoria)
        db.session.commit()

        return categoria.to_dict(), 201


class CategoriaResource(Resource):
    @swag_from({
        "tags": ["Categorías"],
        "summary": "Obtener una categoría por ID",
        "parameters": [
            {
                "in": "path",
                "name": "id",
                "type": "integer",
                "required": True,
            }
        ],
        "responses": {
            200: {"description": "Categoría encontrada"},
            404: {"description": "Categoría no encontrada"},
        },
    })
    def get(self, id):
        categoria = Categoria.query.get(id)

        if not categoria:
            return {"message": "Categoría no encontrada"}, 404

        return categoria.to_dict()

    @swag_from({
        "tags": ["Categorías"],
        "summary": "Actualizar una categoría",
        "parameters": [
            {"in": "path", "name": "id", "type": "integer", "required": True},
            {
                "in": "body",
                "name": "categoria",
                "required": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "nombre": {"type": "string"},
                        "descripcion": {"type": "string"},
                    },
                },
            },
        ],
        "responses": {
            200: {"description": "Categoría actualizada"},
            404: {"description": "Categoría no encontrada"},
        },
    })
    def put(self, id):
        data = request.get_json()
        categoria = Categoria.query.get(id)

        if not categoria:
            return {"message": "Categoría no encontrada"}, 404

        categoria.nombre = data.get("nombre", categoria.nombre)
        categoria.descripcion = data.get("descripcion", categoria.descripcion)
        db.session.commit()

        return categoria.to_dict()

    @swag_from({
        "tags": ["Categorías"],
        "summary": "Eliminar una categoría (solo si no tiene productos)",
        "parameters": [
            {"in": "path", "name": "id", "type": "integer", "required": True},
        ],
        "responses": {
            200: {"description": "Categoría eliminada"},
            400: {"description": "La categoría tiene productos asociados"},
            404: {"description": "Categoría no encontrada"},
        },
    })
    def delete(self, id):
        categoria = Categoria.query.get(id)

        if not categoria:
            return {"message": "Categoría no encontrada"}, 404

        if Producto.query.filter_by(categoria_id=id).count() > 0:
            return {
                "message": "No se puede eliminar: la categoría tiene productos asociados"
            }, 400

        db.session.delete(categoria)
        db.session.commit()

        return {"message": "Categoría eliminada"}
