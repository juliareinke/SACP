from datetime import date
from app import db

class PequenoGrupo(db.Model):
    __tablename__ = "pequenos_grupos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nome = db.Column(
        db.String(150),
        nullable=False
    )

    lider_id = db.Column(
        db.Integer,
        db.ForeignKey("pessoas.id"),
        nullable=True
    )

    dia_semana = db.Column(
        db.String(20),
        nullable=True
    )

    horario = db.Column(
        db.Time,
        nullable=True
    )

    local = db.Column(
        db.String(200),
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

    lider = db.relationship(
        "Pessoa",
        foreign_keys=[lider_id]
    )

    participantes = db.relationship(
        "PessoaPequenoGrupo",
        back_populates="pequeno_grupo",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<PequenoGrupo {self.nome}>"


class PessoaPequenoGrupo(db.Model):
    __tablename__ = "pessoas_pequenos_grupos"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    pessoa_id = db.Column(
        db.Integer,
        db.ForeignKey("pessoas.id"),
        nullable=False
    )

    pequeno_grupo_id = db.Column(
        db.Integer,
        db.ForeignKey("pequenos_grupos.id"),
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
        back_populates="vinculos_pequeno_grupo"
    )

    pequeno_grupo = db.relationship(
        "PequenoGrupo",
        back_populates="participantes"
    )

    def __repr__(self):
        return (
            f"<PessoaPequenoGrupo "
            f"pessoa={self.pessoa_id} "
            f"grupo={self.pequeno_grupo_id}>"
        )