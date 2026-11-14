from app import db


class Discipulado(db.Model):
    __tablename__ = "discipulados"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    pessoa_id = db.Column(
        db.Integer,
        db.ForeignKey("pessoas.id"),
        nullable=False
    )

    discipulador_id = db.Column(
        db.Integer,
        db.ForeignKey("pessoas.id"),
        nullable=False
    )

    data_inicio = db.Column(
        db.Date,
        nullable=False
    )

    data_encerramento = db.Column(
        db.Date,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="ativo"
    )

    observacao = db.Column(
        db.String(500),
        nullable=True
    )

    data_criacao = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now()
    )

    pessoa = db.relationship(
        "Pessoa",
        foreign_keys=[pessoa_id],
        back_populates="discipulados_recebidos"
    )

    discipulador = db.relationship(
        "Pessoa",
        foreign_keys=[discipulador_id],
        back_populates="discipulados_conduzidos"
    )

    def __repr__(self):
        return (
            f"<Discipulado pessoa={self.pessoa_id} "
            f"discipulador={self.discipulador_id}>"
        )