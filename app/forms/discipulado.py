from datetime import date
from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class DiscipuladoForm(FlaskForm):
    pessoa_id = SelectField(
        "Pessoa",
        coerce=int,
        validators=[DataRequired()]
    )

    discipulador_id = SelectField(
        "Discipulador",
        coerce=int,
        validators=[DataRequired()]
    )

    data_inicio = DateField(
        "Data de início",
        validators=[DataRequired()],
        default=date.today
    )

    observacao = TextAreaField(
        "Observação",
        validators=[
            Optional(),
            Length(max=500)
        ]
    )

    submit = SubmitField("Salvar")


class EncerrarDiscipuladoForm(FlaskForm):
    submit = SubmitField("Encerrar discipulado")


class ReabrirDiscipuladoForm(FlaskForm):
    submit = SubmitField("Reabrir discipulado")