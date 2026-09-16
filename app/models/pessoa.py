from app import db


class Pessoa(db.Model):
    __tablename__ = "pessoas"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(150), nullable=False)
    telefone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(254), nullable=True)

    data_nascimento = db.Column(db.Date, nullable=True)
    estado_civil = db.Column(db.String(30), nullable=True)
    tem_filhos = db.Column(db.Boolean, nullable=True)

    situacao_igreja = db.Column(db.String(30), nullable=False)

    ativo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    data_cadastro = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now()
    )

    acompanhamentos = db.relationship(
        "Acompanhamento",
        back_populates="pessoa"
    )

    tarefas = db.relationship(
        "Tarefa",
        back_populates="pessoa"
    )

    def __repr__(self):
        return f"<Pessoa {self.nome}>"