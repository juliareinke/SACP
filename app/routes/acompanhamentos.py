from datetime import date
from flask import Blueprint, flash, redirect, render_template, request,url_for
from flask_login import login_required, current_user
from app import db
from app.forms.acompanhamento import AcompanhamentoForm, EncerrarAcompanhamentoForm, RegistroAcompanhamentoForm
from app.models import Acompanhamento, Pessoa, Usuario, RegistroAcompanhamento


acompanhamentos_bp = Blueprint(
    "acompanhamentos",
    __name__,
    url_prefix="/acompanhamentos"
)


def configurar_choices(form):
    pessoas = db.session.execute(
        db.select(Pessoa).order_by(Pessoa.nome)
    ).scalars().all()

    usuarios = db.session.execute(
        db.select(Usuario)
        .where(Usuario.ativo.is_(True))
        .order_by(Usuario.nome)
    ).scalars().all()

    form.pessoa_id.choices = [
        (pessoa.id, pessoa.nome)
        for pessoa in pessoas
    ]

    form.responsavel_id.choices = [
        (0, "Não definido")
    ] + [
        (usuario.id, usuario.nome)
        for usuario in usuarios
    ]


@acompanhamentos_bp.route("/")
@login_required
def listar():
    status = request.args.get("status", "ativos")

    consulta = db.select(Acompanhamento)

    if status == "ativos":
        consulta = consulta.where(
            Acompanhamento.status == "ativo"
        )

    elif status == "encerrados":
        consulta = consulta.where(
            Acompanhamento.status == "encerrado"
        )

    acompanhamentos = db.session.execute(
        consulta.order_by(
            Acompanhamento.data_inicio.desc()
        )
    ).scalars().all()

    return render_template(
        "acompanhamentos/lista.html",
        acompanhamentos=acompanhamentos,
        status=status
    )


@acompanhamentos_bp.route("/novo", methods=["GET", "POST"])
@login_required
def criar():
    form = AcompanhamentoForm()
    configurar_choices(form)

    pessoa_id = request.args.get(
        "pessoa_id",
        type=int
    )

    if request.method == "GET" and pessoa_id:
        pessoa = db.session.get(Pessoa, pessoa_id)

        if pessoa:
            form.pessoa_id.data = pessoa.id

    if form.validate_on_submit():
        acompanhamento = Acompanhamento(
            pessoa_id=form.pessoa_id.data,
            responsavel_id=(
                form.responsavel_id.data
                if form.responsavel_id.data != 0
                else None
            ),
            tipo=form.tipo.data,
            prioridade=form.prioridade.data,
            data_inicio=form.data_inicio.data,
            observacao=(
                form.observacao.data.strip()
                if form.observacao.data
                else None
            ),
            status="ativo"
        )

        db.session.add(acompanhamento)
        db.session.commit()

        flash(
            "Acompanhamento iniciado com sucesso.",
            "success"
        )

        return redirect(
            url_for(
                "acompanhamentos.detalhe",
                acompanhamento_id=acompanhamento.id
            )
        )

    return render_template(
        "acompanhamentos/formulario.html",
        form=form,
        titulo="Novo acompanhamento"
    )


@acompanhamentos_bp.route("/<int:acompanhamento_id>")
@login_required
def detalhe(acompanhamento_id):
    acompanhamento = db.get_or_404(
        Acompanhamento,
        acompanhamento_id
    )

    encerrar_form = EncerrarAcompanhamentoForm()

    return render_template(
        "acompanhamentos/detalhe.html",
        acompanhamento=acompanhamento,
        encerrar_form=encerrar_form,
        hoje=date.today()
    )


@acompanhamentos_bp.route(
    "/<int:acompanhamento_id>/editar",
    methods=["GET", "POST"]
)
@login_required
def editar(acompanhamento_id):
    acompanhamento = db.get_or_404(
        Acompanhamento,
        acompanhamento_id
    )

    form = AcompanhamentoForm()
    configurar_choices(form)

    if request.method == "GET":
        form.pessoa_id.data = acompanhamento.pessoa_id
        form.tipo.data = acompanhamento.tipo
        form.prioridade.data = acompanhamento.prioridade
        form.responsavel_id.data = (
            acompanhamento.responsavel_id or 0
        )
        form.data_inicio.data = acompanhamento.data_inicio
        form.observacao.data = acompanhamento.observacao

    if form.validate_on_submit():
        acompanhamento.pessoa_id = form.pessoa_id.data

        acompanhamento.responsavel_id = (
            form.responsavel_id.data
            if form.responsavel_id.data != 0
            else None
        )

        acompanhamento.tipo = form.tipo.data
        acompanhamento.prioridade = form.prioridade.data
        acompanhamento.data_inicio = form.data_inicio.data

        acompanhamento.observacao = (
            form.observacao.data.strip()
            if form.observacao.data
            else None
        )

        db.session.commit()

        flash(
            "Acompanhamento atualizado com sucesso.",
            "success"
        )

        return redirect(
            url_for(
                "acompanhamentos.detalhe",
                acompanhamento_id=acompanhamento.id
            )
        )

    return render_template(
        "acompanhamentos/formulario.html",
        form=form,
        titulo="Editar acompanhamento"
    )


@acompanhamentos_bp.route(
    "/<int:acompanhamento_id>/encerrar",
    methods=["POST"]
)
@login_required
def encerrar(acompanhamento_id):
    acompanhamento = db.get_or_404(
        Acompanhamento,
        acompanhamento_id
    )

    form = EncerrarAcompanhamentoForm()

    if form.validate_on_submit():
        acompanhamento.status = "encerrado"
        acompanhamento.data_encerramento = date.today()

        db.session.commit()

        flash(
            "Acompanhamento encerrado com sucesso.",
            "success"
        )

    return redirect(
        url_for(
            "acompanhamentos.detalhe",
            acompanhamento_id=acompanhamento.id
        )
    )
    

@acompanhamentos_bp.route(
    "/<int:acompanhamento_id>/registros/novo",
    methods=["GET", "POST"]
)
@login_required
def criar_registro(acompanhamento_id):
    acompanhamento = db.get_or_404(
        Acompanhamento,
        acompanhamento_id
    )

    if acompanhamento.status != "ativo":
        flash(
            "Não é possível adicionar registros a um acompanhamento encerrado.",
            "error"
        )

        return redirect(
            url_for(
                "acompanhamentos.detalhe",
                acompanhamento_id=acompanhamento.id
            )
        )

    form = RegistroAcompanhamentoForm()

    if form.validate_on_submit():
        registro = RegistroAcompanhamento(
            acompanhamento_id=acompanhamento.id,
            usuario_id=current_user.id,
            tipo=form.tipo.data,
            observacao=(
                form.observacao.data.strip()
                if form.observacao.data
                else None
            )
        )

        db.session.add(registro)
        db.session.commit()

        flash(
            "Registro adicionado ao acompanhamento.",
            "success"
        )

        return redirect(
            url_for(
                "acompanhamentos.detalhe",
                acompanhamento_id=acompanhamento.id
            )
        )

    return render_template(
        "acompanhamentos/registro_formulario.html",
        acompanhamento=acompanhamento,
        form=form
    )