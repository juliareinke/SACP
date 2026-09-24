from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user,
)

from app import db
from app.forms.auth import LoginForm
from app.models import Usuario


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        usuario = db.session.execute(
            db.select(Usuario).where(
                Usuario.email == form.email.data.strip().lower()
            )
        ).scalar_one_or_none()

        if (
            usuario
            and usuario.ativo
            and usuario.verificar_senha(form.senha.data)
        ):
            login_user(usuario)

            flash(
                "Login realizado com sucesso.",
                "success"
            )

            return redirect(url_for("main.index"))

        flash(
            "E-mail ou senha inválidos.",
            "error"
        )

    return render_template(
        "auth/login.html",
        form=form
    )


@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()

    flash(
        "Você saiu do sistema.",
        "success"
    )

    return redirect(url_for("auth.login"))