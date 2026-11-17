from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash
from app import db
from app.models import Pessoa, TurmaEBD, ParticipacaoEBD
from app.forms.ebd import TurmaEBDForm, ParticipanteEBDForm
from app.permissions import roles_required


ebd_bp = Blueprint(
    "ebd",
    __name__,
    url_prefix="/ebd"
)


def configurar_participantes_disponiveis(form):
    vinculos_ativos = db.session.execute(
        db.select(ParticipacaoEBD)
        .where(ParticipacaoEBD.ativo.is_(True))
    ).scalars().all()

    pessoas_com_turma = {
        vinculo.pessoa_id
        for vinculo in vinculos_ativos
    }

    consulta = (
        db.select(Pessoa)
        .where(Pessoa.ativo.is_(True))
        .order_by(Pessoa.nome.asc())
    )

    if pessoas_com_turma:
        consulta = consulta.where(
            Pessoa.id.not_in(pessoas_com_turma)
        )

    pessoas = db.session.execute(
        consulta
    ).scalars().all()

    form.pessoa_id.choices = [
        (pessoa.id, pessoa.nome)
        for pessoa in pessoas
    ]


@ebd_bp.route("/")
@roles_required("admin", "pastoral", "lider")
def listar():
    turmas = db.session.execute(
        db.select(TurmaEBD)
        .order_by(
            TurmaEBD.ativo.desc(),
            TurmaEBD.nome.asc()
        )
    ).scalars().all()

    return render_template(
        "ebd/lista.html",
        turmas=turmas
    )


@ebd_bp.route(
    "/nova",
    methods=["GET", "POST"]
)
@roles_required("admin", "pastoral")
def criar():
    form = TurmaEBDForm()

    if form.validate_on_submit():

        turma = TurmaEBD(
            nome=form.nome.data.strip(),
            descricao=(
                form.descricao.data.strip()
                if form.descricao.data
                else None
            ),
            ativo=True
        )

        db.session.add(turma)
        db.session.commit()

        flash(
            "Turma de EBD criada com sucesso.",
            "success"
        )

        return redirect(
            url_for(
                "ebd.detalhe",
                turma_id=turma.id
            )
        )

    return render_template(
        "ebd/formulario.html",
        form=form,
        titulo="Nova turma de EBD"
    )


@ebd_bp.route("/<int:turma_id>")
@roles_required("admin", "pastoral", "lider")
def detalhe(turma_id):
    turma = db.get_or_404(
        TurmaEBD,
        turma_id
    )

    participantes_ativos = [
        vinculo
        for vinculo in turma.participantes
        if vinculo.ativo
    ]

    form_participante = ParticipanteEBDForm()

    configurar_participantes_disponiveis(
        form_participante
    )

    return render_template(
        "ebd/detalhe.html",
        turma=turma,
        participantes_ativos=participantes_ativos,
        form_participante=form_participante
    )


@ebd_bp.route(
    "/<int:turma_id>/editar",
    methods=["GET", "POST"]
)
@roles_required("admin", "pastoral")
def editar(turma_id):
    turma = db.get_or_404(
        TurmaEBD,
        turma_id
    )

    form = TurmaEBDForm(
        obj=turma
    )

    if form.validate_on_submit():

        turma.nome = form.nome.data.strip()

        turma.descricao = (
            form.descricao.data.strip()
            if form.descricao.data
            else None
        )

        db.session.commit()

        flash(
            "Turma de EBD atualizada.",
            "success"
        )

        return redirect(
            url_for(
                "ebd.detalhe",
                turma_id=turma.id
            )
        )

    return render_template(
        "ebd/formulario.html",
        form=form,
        titulo="Editar turma de EBD",
        turma=turma
    )


@ebd_bp.route(
    "/<int:turma_id>/desativar",
    methods=["POST"]
)
@roles_required("admin", "pastoral")
def desativar(turma_id):
    turma = db.get_or_404(
        TurmaEBD,
        turma_id
    )

    turma.ativo = False

    db.session.commit()

    flash(
        "Turma de EBD desativada.",
        "success"
    )

    return redirect(
        url_for(
            "ebd.detalhe",
            turma_id=turma.id
        )
    )


@ebd_bp.route(
    "/<int:turma_id>/reativar",
    methods=["POST"]
)
@roles_required("admin", "pastoral")
def reativar(turma_id):
    turma = db.get_or_404(
        TurmaEBD,
        turma_id
    )

    turma.ativo = True

    db.session.commit()

    flash(
        "Turma de EBD reativada.",
        "success"
    )

    return redirect(
        url_for(
            "ebd.detalhe",
            turma_id=turma.id
        )
    )


@ebd_bp.route(
    "/<int:turma_id>/participantes/adicionar",
    methods=["POST"]
)
@roles_required("admin", "pastoral")
def adicionar_participante(turma_id):
    turma = db.get_or_404(
        TurmaEBD,
        turma_id
    )

    if not turma.ativo:
        flash(
            "Não é possível adicionar participantes a uma turma inativa.",
            "error"
        )

        return redirect(
            url_for(
                "ebd.detalhe",
                turma_id=turma.id
            )
        )

    form = ParticipanteEBDForm()

    configurar_participantes_disponiveis(
        form
    )

    if form.validate_on_submit():

        existente = db.session.scalar(
            db.select(ParticipacaoEBD)
            .where(
                ParticipacaoEBD.pessoa_id == form.pessoa_id.data,
                ParticipacaoEBD.ativo.is_(True)
            )
        )

        if existente:

            flash(
                "Esta pessoa já participa de uma turma de EBD.",
                "error"
            )

        else:

            participacao = ParticipacaoEBD(
                pessoa_id=form.pessoa_id.data,
                turma_id=turma.id,
                data_entrada=date.today(),
                ativo=True
            )

            db.session.add(participacao)
            db.session.commit()

            flash(
                "Participante adicionado à turma.",
                "success"
            )

    else:

        flash(
            "Não foi possível adicionar o participante.",
            "error"
        )

    return redirect(
        url_for(
            "ebd.detalhe",
            turma_id=turma.id
        )
    )


@ebd_bp.route(
    "/<int:turma_id>/participantes/<int:vinculo_id>/remover",
    methods=["POST"]
)
@roles_required("admin", "pastoral")
def remover_participante(
    turma_id,
    vinculo_id
):
    turma = db.get_or_404(
        TurmaEBD,
        turma_id
    )

    vinculo = db.session.scalar(
        db.select(ParticipacaoEBD)
        .where(
            ParticipacaoEBD.id == vinculo_id,
            ParticipacaoEBD.turma_id == turma.id
        )
    )

    if vinculo is None:
        return "", 404

    if vinculo.ativo:

        vinculo.ativo = False
        vinculo.data_saida = date.today()

        db.session.commit()

        flash(
            "Participante removido da turma.",
            "success"
        )

    return redirect(
        url_for(
            "ebd.detalhe",
            turma_id=turma.id
        )
    )