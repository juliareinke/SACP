from datetime import date
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, Optional


class AcompanhamentoForm(FlaskForm):
    pessoa_id = SelectField(
        "Pessoa",
        coerce=int,
        validators=[InputRequired(message="Selecione uma pessoa.")]
    )

    tipo = SelectField(
        "Tipo de acompanhamento",
        choices=[
            ("visitante", "Acompanhamento de visitante"),
            ("novo_crente", "Novo na fé"),
            ("pastoral", "Acompanhamento pastoral"),
            ("retorno", "Retorno de contato"),
            ("outro", "Outro"),
        ],
        validators=[DataRequired()]
    )

    prioridade = SelectField(
        "Prioridade",
        choices=[
            ("baixa", "Baixa"),
            ("normal", "Normal"),
            ("alta", "Alta"),
            ("urgente", "Urgente"),
        ],
        default="normal",
        validators=[DataRequired()]
    )

    responsavel_id = SelectField(
        "Responsável",
        coerce=int,
        validators=[Optional()]
    )

    data_inicio = DateField(
        "Data de início",
        default=date.today,
        validators=[DataRequired()]
    )

    observacao = TextAreaField(
        "Observação",
        validators=[
            Optional(),
            Length(max=1000)
        ]
    )

    submit = SubmitField("Salvar")


class EncerrarAcompanhamentoForm(FlaskForm):
    submit = SubmitField("Encerrar acompanhamento")