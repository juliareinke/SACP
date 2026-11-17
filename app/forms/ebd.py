from flask_wtf import FlaskForm
from wtforms import StringField, SelectField,SubmitField
from wtforms.validators import DataRequired, Length, Optional

class TurmaEBDForm(FlaskForm):
    nome = StringField(
        "Nome da turma",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )
    descricao = StringField(
        "Descrição",
        validators=[
            Optional(),
            Length(max=300)
        ]
    )
    submit = SubmitField("Salvar")


class ParticipanteEBDForm(FlaskForm):
    pessoa_id = SelectField(
        "Pessoa",
        coerce=int,
        validators=[DataRequired()]
    )
    submit = SubmitField("Adicionar participante")