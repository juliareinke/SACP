from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user
from app import db
from app.models import Usuario
from app.forms.usuario import CriarUsuarioForm, EditarUsuarioForm
from app.permissions import roles_required


usuarios_bp = Blueprint(
    "usuarios",
    __name__,
    url_prefix="/usuarios"
)


@usuarios_bp.route("/")
@roles_required("admin")
def listar():
    usuarios = db.session.execute(
        db.select(Usuario)
        .order_by(
            Usuario.ativo.desc(),
            Usuario.nome.asc()
        )
    ).scalars().all()

    return render_template(
        "usuarios/lista.html",
        usuarios=usuarios
    )


@usuarios_bp.route("/novo", methods=["GET", "POST"])
@roles_required("admin")
def criar():
    form = CriarUsuarioForm()

    if form.validate_on_submit():

        email = form.email.data.strip().lower()

        usuario_existente = db.session.scalar(
            db.select(Usuario)
            .where(Usuario.email == email)
        )

        if usuario_existente:
            form.email.errors.append(
                "Já existe um usuário com este e-mail."
            )

        else:
            usuario = Usuario(
                nome=form.nome.data.strip(),
                email=email,
                perfil=form.perfil.data,
                ativo=True
            )

            usuario.definir_senha(form.senha.data)

            db.session.add(usuario)
            db.session.commit()

            flash(
                "Usuário criado com sucesso.",
                "success"
            )

            return redirect(
                url_for("usuarios.listar")
            )

    return render_template(
        "usuarios/formulario.html",
        form=form,
        titulo="Novo usuário",
        modo="criar"
    )


@usuarios_bp.route(
    "/<int:usuario_id>/editar",
    methods=["GET", "POST"]
)
@roles_required("admin")
def editar(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)

    form = EditarUsuarioForm(obj=usuario)

    if form.validate_on_submit():

        email = form.email.data.strip().lower()

        usuario_existente = db.session.scalar(
            db.select(Usuario)
            .where(
                Usuario.email == email,
                Usuario.id != usuario.id
            )
        )

        if usuario_existente:
            form.email.errors.append(
                "Já existe um usuário com este e-mail."
            )

        else:
            usuario.nome = form.nome.data.strip()
            usuario.email = email
            usuario.perfil = form.perfil.data

            if form.nova_senha.data:
                usuario.definir_senha(
                    form.nova_senha.data
                )

            db.session.commit()

            flash(
                "Usuário atualizado com sucesso.",
                "success"
            )

            return redirect(
                url_for("usuarios.listar")
            )

    return render_template(
        "usuarios/formulario.html",
        form=form,
        titulo="Editar usuário",
        modo="editar",
        usuario=usuario
    )


@usuarios_bp.route(
    "/<int:usuario_id>/desativar",
    methods=["POST"]
)
@roles_required("admin")
def desativar(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)

    if usuario.id == current_user.id:
        flash(
            "Você não pode desativar seu próprio usuário.",
            "error"
        )

        return redirect(
            url_for("usuarios.listar")
        )

    usuario.ativo = False

    db.session.commit()

    flash(
        "Usuário desativado.",
        "success"
    )

    return redirect(
        url_for("usuarios.listar")
    )


@usuarios_bp.route(
    "/<int:usuario_id>/reativar",
    methods=["POST"]
)
@roles_required("admin")
def reativar(usuario_id):
    usuario = db.get_or_404(Usuario, usuario_id)

    usuario.ativo = True

    db.session.commit()

    flash(
        "Usuário reativado.",
        "success"
    )

    return redirect(
        url_for("usuarios.listar")
    )