from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class PessoaForm(FlaskForm):
    nome = StringField(
        "Nome",
        validators=[
            DataRequired(message="Informe o nome."),
            Length(max=150)
        ]
    )

    telefone = StringField(
        "Telefone",
        validators=[
            Optional(),
            Length(max=30)
        ]
    )

    email = StringField(
        "E-mail",
        validators=[
            Optional(),
            Email(message="Informe um e-mail válido."),
            Length(max=254)
        ]
    )

    data_nascimento = DateField(
        "Data de nascimento",
        validators=[Optional()]
    )

    estado_civil = SelectField(
        "Estado civil",
        choices=[
            ("", "Não informado"),
            ("solteiro", "Solteiro(a)"),
            ("casado", "Casado(a)"),
            ("viuvo", "Viúvo(a)"),
            ("divorciado", "Divorciado(a)"),
            ("outro", "Outro"),
        ],
        validators=[Optional()]
    )

    tem_filhos = SelectField(
        "Tem filhos?",
        choices=[
            ("", "Não informado"),
            ("sim", "Sim"),
            ("nao", "Não"),
        ],
        validators=[Optional()]
    )

    situacao_igreja = SelectField(
        "Situação na igreja",
        choices=[
            ("visitante", "Visitante"),
            ("congregado", "Congregado(a)"),
            ("membro", "Membro"),
        ],
        validators=[
            DataRequired(message="Informe a situação na igreja.")
        ]
    )

    submit = SubmitField("Salvar")


class InativarPessoaForm(FlaskForm):
    submit = SubmitField("Inativar")
    
class ReativarPessoaForm(FlaskForm):
    submit = SubmitField("Reativar")