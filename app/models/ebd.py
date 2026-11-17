from datetime import date
from app import db


class TurmaEBD(db.Model):
    __tablename__ = "turmas_ebd"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(150),
        nullable=False
    )

    descricao = db.Column(
        db.String(300),
        nullable=True
    )

    ativo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    data_criacao = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now()
    )

    participantes = db.relationship(
        "ParticipacaoEBD",
        back_populates="turma",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<TurmaEBD {self.nome}>"


class ParticipacaoEBD(db.Model):
    __tablename__ = "participacoes_ebd"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    pessoa_id = db.Column(
        db.Integer,
        db.ForeignKey("pessoas.id"),
        nullable=False
    )

    turma_id = db.Column(
        db.Integer,
        db.ForeignKey("turmas_ebd.id"),
        nullable=False
    )

    data_entrada = db.Column(
        db.Date,
        nullable=False,
        default=date.today
    )

    data_saida = db.Column(
        db.Date,
        nullable=True
    )

    ativo = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    pessoa = db.relationship(
        "Pessoa",
        back_populates="participacoes_ebd"
    )

    turma = db.relationship(
        "TurmaEBD",
        back_populates="participantes"
    )

    def __repr__(self):
        return (
            f"<ParticipacaoEBD "
            f"pessoa={self.pessoa_id} "
            f"turma={self.turma_id}>"
        )