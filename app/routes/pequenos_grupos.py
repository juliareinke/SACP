from flask import Blueprint, render_template, redirect, url_for, flash
from app import db
from app.models import Pessoa, PequenoGrupo, PessoaPequenoGrupo
from app.forms.pequeno_grupo import PequenoGrupoForm, ParticipantePequenoGrupoForm
from app.permissions import roles_required
from datetime import date

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

    form_participante = ParticipantePequenoGrupoForm()
    configurar_participantes_disponiveis(
        form_participante
    )

    return render_template(
        "pequenos_grupos/detalhe.html",
        grupo=grupo,
        participantes_ativos=participantes_ativos,
        form_participante=form_participante
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
    
    
def configurar_participantes_disponiveis(form):
    vinculos_ativos = db.session.execute(
        db.select(PessoaPequenoGrupo)
        .where(PessoaPequenoGrupo.ativo.is_(True))
    ).scalars().all()

    pessoas_com_pg = {
        vinculo.pessoa_id
        for vinculo in vinculos_ativos
    }

    pessoas = db.session.execute(
        db.select(Pessoa)
        .where(
            Pessoa.ativo.is_(True),
            Pessoa.id.not_in(pessoas_com_pg)
        )
        .order_by(Pessoa.nome.asc())
    ).scalars().all()

    form.pessoa_id.choices = [
        (pessoa.id, pessoa.nome)
        for pessoa in pessoas
    ]
    

@pequenos_grupos_bp.route(
    "/<int:grupo_id>/participantes/adicionar",
    methods=["POST"]
)
@roles_required("admin", "pastoral")
def adicionar_participante(grupo_id):
    grupo = db.get_or_404(
        PequenoGrupo,
        grupo_id
    )

    if not grupo.ativo:
        flash(
            "Não é possível adicionar participantes a um grupo inativo.",
            "error"
        )
        return redirect(
            url_for(
                "pequenos_grupos.detalhe",
                grupo_id=grupo.id
            )
        )

    form = ParticipantePequenoGrupoForm()
    configurar_participantes_disponiveis(form)

    if form.validate_on_submit():

        vinculo_existente = db.session.scalar(
            db.select(PessoaPequenoGrupo)
            .where(
                PessoaPequenoGrupo.pessoa_id == form.pessoa_id.data,
                PessoaPequenoGrupo.ativo.is_(True)
            )
        )

        if vinculo_existente:
            flash(
                "Esta pessoa já participa de um Pequeno Grupo.",
                "error"
            )

        else:
            vinculo = PessoaPequenoGrupo(
                pessoa_id=form.pessoa_id.data,
                pequeno_grupo_id=grupo.id,
                data_entrada=date.today(),
                ativo=True
            )

            db.session.add(vinculo)
            db.session.commit()

            flash(
                "Participante adicionado ao grupo.",
                "success"
            )

    else:
        flash(
            "Não foi possível adicionar o participante.",
            "error"
        )

    return redirect(
        url_for(
            "pequenos_grupos.detalhe",
            grupo_id=grupo.id
        )
    )


@pequenos_grupos_bp.route(
    "/<int:grupo_id>/participantes/<int:vinculo_id>/remover",
    methods=["POST"]
)
@roles_required("admin", "pastoral")
def remover_participante(grupo_id, vinculo_id):
    grupo = db.get_or_404(
        PequenoGrupo,
        grupo_id
    )

    vinculo = db.session.scalar(
        db.select(PessoaPequenoGrupo)
        .where(
            PessoaPequenoGrupo.id == vinculo_id,
            PessoaPequenoGrupo.pequeno_grupo_id == grupo.id
        )
    )

    if vinculo is None:
        return "", 404

    if not vinculo.ativo:
        flash(
            "Este participante já não faz parte do grupo.",
            "error"
        )

    else:
        vinculo.ativo = False
        vinculo.data_saida = date.today()

        db.session.commit()

        flash(
            "Participante removido do grupo.",
            "success"
        )

    return redirect(
        url_for(
            "pequenos_grupos.detalhe",
            grupo_id=grupo.id
        )
    )