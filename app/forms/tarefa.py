from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, Length, Optional


class TarefaForm(FlaskForm):
    titulo = StringField(
        "Título",
        validators=[
            DataRequired(message="Informe o título da tarefa."),
            Length(max=150)
        ]
    )

    descricao = TextAreaField(
        "Descrição",
        validators=[
            Optional(),
            Length(max=1000)
        ]
    )

    pessoa_id = SelectField(
        "Pessoa",
        coerce=int,
        validators=[
            InputRequired(message="Selecione uma pessoa.")
        ]
    )

    acompanhamento_id = SelectField(
        "Acompanhamento",
        coerce=int,
        validators=[Optional()]
    )

    responsavel_id = SelectField(
        "Responsável",
        coerce=int,
        validators=[
            InputRequired(message="Selecione um responsável.")
        ]
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

    prazo = DateField(
        "Prazo",
        validators=[
            DataRequired(message="Informe o prazo.")
        ]
    )

    submit = SubmitField("Salvar")


class ConcluirTarefaForm(FlaskForm):
    submit = SubmitField("Concluir tarefa")


class ReabrirTarefaForm(FlaskForm):
    submit = SubmitField("Reabrir tarefa")