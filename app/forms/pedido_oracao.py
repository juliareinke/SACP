from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class PedidoOracaoForm(FlaskForm):
    motivo = StringField(
        "Motivo / assunto",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )

    pessoa_id = SelectField(
        "Pessoa relacionada",
        coerce=int,
        validators=[Optional()]
    )

    responsavel_id = SelectField(
        "Responsável",
        coerce=int,
        validators=[Optional()]
    )

    data_pedido = DateField(
        "Data do pedido",
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


class EncerrarPedidoOracaoForm(FlaskForm):
    submit = SubmitField("Encerrar pedido")


class ReabrirPedidoOracaoForm(FlaskForm):
    submit = SubmitField("Reabrir pedido")