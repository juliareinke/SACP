from app import db


class Acompanhamento(db.Model):
    __tablename__ = "acompanhamentos"

    id = db.Column(db.Integer, primary_key=True)

    pessoa_id = db.Column(
        db.Integer,
        db.ForeignKey("pessoas.id"),
        nullable=False
    )

    responsavel_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=True
    )

    tipo = db.Column(
        db.String(50),
        nullable=False
    )

    prioridade = db.Column(
        db.String(20),
        nullable=False,
        default="normal"
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="ativo"
    )

    data_inicio = db.Column(
        db.Date,
        nullable=False
    )

    data_encerramento = db.Column(
        db.Date,
        nullable=True
    )

    observacao = db.Column(
        db.Text,
        nullable=True
    )

    pessoa = db.relationship(
        "Pessoa",
        back_populates="acompanhamentos"
    )

    responsavel = db.relationship(
        "Usuario",
        back_populates="acompanhamentos"
    )

    registros = db.relationship(
        "RegistroAcompanhamento",
        back_populates="acompanhamento"
    )

    tarefas = db.relationship(
        "Tarefa",
        back_populates="acompanhamento"
    )

    def __repr__(self):
        return f"<Acompanhamento {self.id} - Pessoa {self.pessoa_id}>"


class RegistroAcompanhamento(db.Model):
    __tablename__ = "registros_acompanhamento"

    id = db.Column(db.Integer, primary_key=True)

    acompanhamento_id = db.Column(
        db.Integer,
        db.ForeignKey("acompanhamentos.id"),
        nullable=False
    )

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=False
    )

    data = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now()
    )

    tipo = db.Column(
        db.String(50),
        nullable=False
    )

    observacao = db.Column(
        db.Text,
        nullable=True
    )

    acompanhamento = db.relationship(
        "Acompanhamento",
        back_populates="registros"
    )

    usuario = db.relationship(
        "Usuario",
        back_populates="registros"
    )

    def __repr__(self):
        return f"<RegistroAcompanhamento {self.id}>"