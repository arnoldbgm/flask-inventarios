import os

from dotenv import load_dotenv
from flask import Flask
from flask_restful import Api
from flasgger import Swagger

from db import db, migrate
from models import Categoria, Producto, MovimientoStock
from resources import (
    CategoriaListResource,
    CategoriaResource,
    ProductoListResource,
    ProductoResource,
    MovimientoListResource,
    MovimientoResource,
)

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

db.init_app(app)
migrate.init_app(app, db)

Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "API de Gestion de Inventario",
        "description": (
            "API para gestionar categorias, productos y movimientos de stock. "
            "Ejemplo didactico para deploy en Render."
        ),
        "version": "1.0.0",
    },
    "basePath": "/",
    "schemes": ["http", "https"],
})

api = Api(app)

api.add_resource(CategoriaListResource, "/categorias")
api.add_resource(CategoriaResource, "/categorias/<int:id>")

api.add_resource(ProductoListResource, "/productos")
api.add_resource(ProductoResource, "/productos/<int:id>")

api.add_resource(MovimientoListResource, "/movimientos")
api.add_resource(MovimientoResource, "/movimientos/<int:id>")


@app.route("/")
def home():
    return {
        "message": "API de Gestion de Inventario",
        "docs": "/apidocs/",
        "endpoints": {
            "categorias": "/categorias",
            "productos": "/productos",
            "movimientos": "/movimientos",
        },
    }


if __name__ == "__main__":
    app.run(debug=True)
