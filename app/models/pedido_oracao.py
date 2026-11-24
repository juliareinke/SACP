from datetime import date
from app import db


class PedidoOracao(db.Model):
    __tablename__ = "pedidos_oracao"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    pessoa_id = db.Column(
        db.Integer,
        db.ForeignKey("pessoas.id"),
        nullable=True
    )

    responsavel_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=True
    )

    motivo = db.Column(
        db.String(150),
        nullable=False
    )

    observacao = db.Column(
        db.String(500),
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="ativo"
    )

    data_pedido = db.Column(
        db.Date,
        nullable=False,
        default=date.today
    )

    data_encerramento = db.Column(
        db.Date,
        nullable=True
    )

    data_criacao = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now()
    )

    pessoa = db.relationship(
        "Pessoa"
    )

    responsavel = db.relationship(
        "Usuario"
    )

    def __repr__(self):
        return f"<PedidoOracao {self.id} - {self.motivo}>"