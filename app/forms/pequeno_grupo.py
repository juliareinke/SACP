from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TimeField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


DIAS_SEMANA = [
    ("", "Não informado"),
    ("segunda", "Segunda-feira"),
    ("terca", "Terça-feira"),
    ("quarta", "Quarta-feira"),
    ("quinta", "Quinta-feira"),
    ("sexta", "Sexta-feira"),
    ("sabado", "Sábado"),
    ("domingo", "Domingo"),
]


class PequenoGrupoForm(FlaskForm):
    nome = StringField(
        "Nome",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )

    lider_id = SelectField(
        "Líder",
        coerce=int,
        validators=[Optional()]
    )

    dia_semana = SelectField(
        "Dia da semana",
        choices=DIAS_SEMANA,
        validators=[Optional()]
    )

    horario = TimeField(
        "Horário",
        validators=[Optional()]
    )

    local = StringField(
        "Local",
        validators=[
            Optional(),
            Length(max=200)
        ]
    )

    submit = SubmitField("Salvar")