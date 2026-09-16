from app import db


class Tarefa(db.Model):
    __tablename__ = "tarefas"

    id = db.Column(db.Integer, primary_key=True)

    pessoa_id = db.Column(
        db.Integer,
        db.ForeignKey("pessoas.id"),
        nullable=False
    )

    acompanhamento_id = db.Column(
        db.Integer,
        db.ForeignKey("acompanhamentos.id"),
        nullable=True
    )

    responsavel_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    titulo = db.Column(
        db.String(150),
        nullable=False
    )

    descricao = db.Column(
        db.Text,
        nullable=True
    )

    prioridade = db.Column(
        db.String(20),
        nullable=False,
        default="normal"
    )

    prazo = db.Column(
        db.Date,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="pendente"
    )

    data_criacao = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now()
    )

    data_conclusao = db.Column(
        db.DateTime(timezone=True),
        nullable=True
    )

    pessoa = db.relationship(
        "Pessoa",
        back_populates="tarefas"
    )

    acompanhamento = db.relationship(
        "Acompanhamento",
        back_populates="tarefas"
    )

    responsavel = db.relationship(
        "Usuario",
        back_populates="tarefas"
    )

    def __repr__(self):
        return f"<Tarefa {self.titulo}>"