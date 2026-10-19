from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SelectField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional
)


PERFIS = [
    ("admin", "Administrador"),
    ("pastoral", "Liderança pastoral"),
    ("lider", "Líder"),
    ("recepcao", "Recepção"),
]


class CriarUsuarioForm(FlaskForm):
    nome = StringField(
        "Nome",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )

    email = StringField(
        "E-mail",
        validators=[
            DataRequired(),
            Email(),
            Length(max=254)
        ]
    )

    senha = PasswordField(
        "Senha",
        validators=[
            DataRequired(),
            Length(min=8, max=128)
        ]
    )

    perfil = SelectField(
        "Perfil",
        choices=PERFIS,
        validators=[DataRequired()]
    )

    submit = SubmitField("Criar usuário")


class EditarUsuarioForm(FlaskForm):
    nome = StringField(
        "Nome",
        validators=[
            DataRequired(),
            Length(max=150)
        ]
    )

    email = StringField(
        "E-mail",
        validators=[
            DataRequired(),
            Email(),
            Length(max=254)
        ]
    )

    perfil = SelectField(
        "Perfil",
        choices=PERFIS,
        validators=[DataRequired()]
    )

    nova_senha = PasswordField(
        "Nova senha",
        validators=[
            Optional(),
            Length(min=8, max=128)
        ]
    )

    submit = SubmitField("Salvar alterações")