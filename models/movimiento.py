from datetime import datetime, timezone

from db import db


class MovimientoStock(db.Model):
    __tablename__ = "movimientos_stock"

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    motivo = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "producto_id": self.producto_id,
            "tipo": self.tipo,
            "cantidad": self.cantidad,
            "fecha": self.fecha.isoformat(),
            "motivo": self.motivo,
        }
