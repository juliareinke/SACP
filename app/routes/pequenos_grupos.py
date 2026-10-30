from flask import Blueprint, render_template, redirect, url_for, flash
from app import db
from app.models import Pessoa, PequenoGrupo
from app.forms.pequeno_grupo import PequenoGrupoForm
from app.permissions import roles_required


pequenos_grupos_bp = Blueprint(
    "pequenos_grupos",
    __name__,
    url_prefix="/pequenos-grupos"
)


def configurar_lideres(form):
    pessoas = db.session.execute(
        db.select(Pessoa)
        .where(Pessoa.ativo.is_(True))
        .order_by(Pessoa.nome.asc())
    ).scalars().all()

    form.lider_id.choices = [
        (0, "Não definido")
    ] + [
        (pessoa.id, pessoa.nome)
        for pessoa in pessoas
    ]


@pequenos_grupos_bp.route("/")
@roles_required("admin", "pastoral", "lider")
def listar():
    grupos = db.session.execute(
        db.select(PequenoGrupo)
        .order_by(
            PequenoGrupo.ativo.desc(),
            PequenoGrupo.nome.asc()
        )
    ).scalars().all()

    return render_template(
        "pequenos_grupos/lista.html",
        grupos=grupos
    )


@pequenos_grupos_bp.route(
    "/novo",
    methods=["GET", "POST"]
)
@roles_required("admin", "pastoral")
def criar():
    form = PequenoGrupoForm()

    configurar_lideres(form)

    if form.validate_on_submit():

        grupo = PequenoGrupo(
            nome=form.nome.data.strip(),
            lider_id=(
                form.lider_id.data
                if form.lider_id.data != 0
                else None
            ),
            dia_semana=form.dia_semana.data or None,
            horario=form.horario.data,
            local=(
                form.local.data.strip()
                if form.local.data
                else None
            ),
            ativo=True
        )

        db.session.add(grupo)
        db.session.commit()

        flash(
            "Pequeno Grupo criado com sucesso.",
            "success"
        )

        return redirect(
            url_for(
                "pequenos_grupos.detalhe",
                grupo_id=grupo.id
            )
        )

    return render_template(
        "pequenos_grupos/formulario.html",
        form=form,
        titulo="Novo Pequeno Grupo"
    )


@pequenos_grupos_bp.route("/<int:grupo_id>")
@roles_required("admin", "pastoral", "lider")
def detalhe(grupo_id):
    grupo = db.get_or_404(
        PequenoGrupo,
        grupo_id
    )

    participantes_ativos = [
        vinculo
        for vinculo in grupo.participantes
        if vinculo.ativo
    ]

    return render_template(
        "pequenos_grupos/detalhe.html",
        grupo=grupo,
        participantes_ativos=participantes_ativos
    )


@pequenos_grupos_bp.route(
    "/<int:grupo_id>/editar",
    methods=["GET", "POST"]
)
@roles_required("admin", "pastoral")
def editar(grupo_id):
    grupo = db.get_or_404(
        PequenoGrupo,
        grupo_id
    )

    form = PequenoGrupoForm(obj=grupo)

    configurar_lideres(form)

    if form.validate_on_submit():

        grupo.nome = form.nome.data.strip()

        grupo.lider_id = (
            form.lider_id.data
            if form.lider_id.data != 0
            else None
        )

        grupo.dia_semana = (
            form.dia_semana.data or None
        )

        grupo.horario = form.horario.data

        grupo.local = (
            form.local.data.strip()
            if form.local.data
            else None
        )

        db.session.commit()

        flash(
            "Pequeno Grupo atualizado.",
            "success"
        )

        return redirect(
            url_for(
                "pequenos_grupos.detalhe",
                grupo_id=grupo.id
            )
        )

    if not form.is_submitted():
        form.lider_id.data = grupo.lider_id or 0

    return render_template(
        "pequenos_grupos/formulario.html",
        form=form,
        titulo="Editar Pequeno Grupo",
        grupo=grupo
    )


@pequenos_grupos_bp.route(
    "/<int:grupo_id>/desativar",
    methods=["POST"]
)
@roles_required("admin", "pastoral")
def desativar(grupo_id):
    grupo = db.get_or_404(
        PequenoGrupo,
        grupo_id
    )

    grupo.ativo = False

    db.session.commit()

    flash(
        "Pequeno Grupo desativado.",
        "success"
    )

    return redirect(
        url_for(
            "pequenos_grupos.detalhe",
            grupo_id=grupo.id
        )
    )


@pequenos_grupos_bp.route(
    "/<int:grupo_id>/reativar",
    methods=["POST"]
)
@roles_required("admin", "pastoral")
def reativar(grupo_id):
    grupo = db.get_or_404(
        PequenoGrupo,
        grupo_id
    )

    grupo.ativo = True

    db.session.commit()

    flash(
        "Pequeno Grupo reativado.",
        "success"
    )

    return redirect(
        url_for(
            "pequenos_grupos.detalhe",
            grupo_id=grupo.id
        )
    )