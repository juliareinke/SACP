from datetime import date, datetime, timezone
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app import db
from app.forms.tarefa import ConcluirTarefaForm, ReabrirTarefaForm, TarefaForm
from app.models import Acompanhamento, Pessoa, Tarefa, Usuario


tarefas_bp = Blueprint(
    "tarefas",
    __name__,
    url_prefix="/tarefas"
)


def configurar_choices(form):
    pessoas = db.session.execute(
        db.select(Pessoa)
        .where(Pessoa.ativo.is_(True))
        .order_by(Pessoa.nome)
    ).scalars().all()

    usuarios = db.session.execute(
        db.select(Usuario)
        .where(Usuario.ativo.is_(True))
        .order_by(Usuario.nome)
    ).scalars().all()

    acompanhamentos = db.session.execute(
        db.select(Acompanhamento)
        .where(Acompanhamento.status == "ativo")
        .order_by(Acompanhamento.data_inicio.desc())
    ).scalars().all()

    form.pessoa_id.choices = [
        (pessoa.id, pessoa.nome)
        for pessoa in pessoas
    ]

    form.responsavel_id.choices = [
        (usuario.id, usuario.nome)
        for usuario in usuarios
    ]

    form.acompanhamento_id.choices = [
        (0, "Sem acompanhamento específico")
    ] + [
        (
            acompanhamento.id,
            f"{acompanhamento.pessoa.nome} — "
            f"{acompanhamento.tipo.replace('_', ' ').capitalize()}"
        )
        for acompanhamento in acompanhamentos
    ]


def validar_acompanhamento(form):
    if form.acompanhamento_id.data == 0:
        return None

    acompanhamento = db.session.get(
        Acompanhamento,
        form.acompanhamento_id.data
    )

    if not acompanhamento:
        form.acompanhamento_id.errors.append(
            "Acompanhamento inválido."
        )
        return False

    if acompanhamento.pessoa_id != form.pessoa_id.data:
        form.acompanhamento_id.errors.append(
            "O acompanhamento selecionado não pertence à pessoa escolhida."
        )
        return False

    if acompanhamento.status != "ativo":
        form.acompanhamento_id.errors.append(
            "Não é possível vincular uma tarefa a um acompanhamento encerrado."
        )
        return False

    return acompanhamento


@tarefas_bp.route("/")
@login_required
def listar():
    status = request.args.get("status", "pendentes")

    consulta = db.select(Tarefa)

    if status == "pendentes":
        consulta = consulta.where(
            Tarefa.status == "pendente"
        )

    elif status == "atrasadas":
        consulta = consulta.where(
            Tarefa.status == "pendente",
            Tarefa.prazo < date.today()
        )

    elif status == "concluidas":
        consulta = consulta.where(
            Tarefa.status == "concluida"
        )

    tarefas = db.session.execute(
        consulta.order_by(Tarefa.prazo.asc())
    ).scalars().all()

    return render_template(
        "tarefas/lista.html",
        tarefas=tarefas,
        status=status,
        hoje=date.today()
    )


@tarefas_bp.route("/nova", methods=["GET", "POST"])
@login_required
def criar():
    form = TarefaForm()
    configurar_choices(form)

    pessoa_id = request.args.get(
        "pessoa_id",
        type=int
    )

    acompanhamento_id = request.args.get(
        "acompanhamento_id",
        type=int
    )

    if request.method == "GET":
        form.responsavel_id.data = current_user.id

        if acompanhamento_id:
            acompanhamento = db.session.get(
                Acompanhamento,
                acompanhamento_id
            )

            if acompanhamento:
                form.acompanhamento_id.data = acompanhamento.id
                form.pessoa_id.data = acompanhamento.pessoa_id

        elif pessoa_id:
            pessoa = db.session.get(Pessoa, pessoa_id)

            if pessoa:
                form.pessoa_id.data = pessoa.id

    if form.validate_on_submit():
        acompanhamento = validar_acompanhamento(form)

        if acompanhamento is not False:
            tarefa = Tarefa(
                titulo=form.titulo.data.strip(),
                descricao=(
                    form.descricao.data.strip()
                    if form.descricao.data
                    else None
                ),
                pessoa_id=form.pessoa_id.data,
                acompanhamento_id=(
                    acompanhamento.id
                    if acompanhamento
                    else None
                ),
                responsavel_id=form.responsavel_id.data,
                prioridade=form.prioridade.data,
                prazo=form.prazo.data,
                status="pendente"
            )

            db.session.add(tarefa)
            db.session.commit()

            flash(
                "Tarefa criada com sucesso.",
                "success"
            )

            return redirect(
                url_for(
                    "tarefas.detalhe",
                    tarefa_id=tarefa.id
                )
            )

    return render_template(
        "tarefas/formulario.html",
        form=form,
        titulo="Nova tarefa"
    )


@tarefas_bp.route("/<int:tarefa_id>")
@login_required
def detalhe(tarefa_id):
    tarefa = db.get_or_404(Tarefa, tarefa_id)

    concluir_form = ConcluirTarefaForm()
    reabrir_form = ReabrirTarefaForm()

    return render_template(
        "tarefas/detalhe.html",
        tarefa=tarefa,
        hoje=date.today(),
        concluir_form=concluir_form,
        reabrir_form=reabrir_form
    )


@tarefas_bp.route(
    "/<int:tarefa_id>/editar",
    methods=["GET", "POST"]
)
@login_required
def editar(tarefa_id):
    tarefa = db.get_or_404(Tarefa, tarefa_id)

    if tarefa.status == "concluida":
        flash(
            "Reabra a tarefa antes de editá-la.",
            "error"
        )

        return redirect(
            url_for(
                "tarefas.detalhe",
                tarefa_id=tarefa.id
            )
        )

    form = TarefaForm()
    configurar_choices(form)

    if request.method == "GET":
        form.titulo.data = tarefa.titulo
        form.descricao.data = tarefa.descricao
        form.pessoa_id.data = tarefa.pessoa_id
        form.acompanhamento_id.data = (
            tarefa.acompanhamento_id or 0
        )
        form.responsavel_id.data = tarefa.responsavel_id
        form.prioridade.data = tarefa.prioridade
        form.prazo.data = tarefa.prazo

    if form.validate_on_submit():
        acompanhamento = validar_acompanhamento(form)

        if acompanhamento is not False:
            tarefa.titulo = form.titulo.data.strip()

            tarefa.descricao = (
                form.descricao.data.strip()
                if form.descricao.data
                else None
            )

            tarefa.pessoa_id = form.pessoa_id.data

            tarefa.acompanhamento_id = (
                acompanhamento.id
                if acompanhamento
                else None
            )

            tarefa.responsavel_id = form.responsavel_id.data
            tarefa.prioridade = form.prioridade.data
            tarefa.prazo = form.prazo.data

            db.session.commit()

            flash(
                "Tarefa atualizada com sucesso.",
                "success"
            )

            return redirect(
                url_for(
                    "tarefas.detalhe",
                    tarefa_id=tarefa.id
                )
            )

    return render_template(
        "tarefas/formulario.html",
        form=form,
        titulo="Editar tarefa"
    )


@tarefas_bp.route(
    "/<int:tarefa_id>/concluir",
    methods=["POST"]
)
@login_required
def concluir(tarefa_id):
    tarefa = db.get_or_404(Tarefa, tarefa_id)
    form = ConcluirTarefaForm()

    if form.validate_on_submit():
        tarefa.status = "concluida"
        tarefa.data_conclusao = datetime.now(timezone.utc)

        db.session.commit()

        flash(
            "Tarefa concluída com sucesso.",
            "success"
        )

    return redirect(
        url_for(
            "tarefas.detalhe",
            tarefa_id=tarefa.id
        )
    )


@tarefas_bp.route(
    "/<int:tarefa_id>/reabrir",
    methods=["POST"]
)
@login_required
def reabrir(tarefa_id):
    tarefa = db.get_or_404(Tarefa, tarefa_id)
    form = ReabrirTarefaForm()

    if form.validate_on_submit():
        tarefa.status = "pendente"
        tarefa.data_conclusao = None

        db.session.commit()

        flash(
            "Tarefa reaberta com sucesso.",
            "success"
        )

    return redirect(
        url_for(
            "tarefas.detalhe",
            tarefa_id=tarefa.id
        )
    )