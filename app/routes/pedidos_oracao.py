from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from app import db
from app.models import Pessoa, Usuario, PedidoOracao
from app.forms.pedido_oracao import PedidoOracaoForm, EncerrarPedidoOracaoForm, ReabrirPedidoOracaoForm
from app.permissions import roles_required


pedidos_oracao_bp = Blueprint(
    "pedidos_oracao",
    __name__,
    url_prefix="/pedidos-oracao"
)


def configurar_choices(form):
    pessoas = db.session.execute(
        db.select(Pessoa)
        .where(Pessoa.ativo.is_(True))
        .order_by(Pessoa.nome.asc())
    ).scalars().all()

    usuarios = db.session.execute(
        db.select(Usuario)
        .where(Usuario.ativo.is_(True))
        .order_by(Usuario.nome.asc())
    ).scalars().all()

    form.pessoa_id.choices = [
        (0, "Não vinculada")
    ] + [
        (pessoa.id, pessoa.nome)
        for pessoa in pessoas
    ]

    form.responsavel_id.choices = [
        (0, "Não definido")
    ] + [
        (usuario.id, usuario.nome)
        for usuario in usuarios
    ]


@pedidos_oracao_bp.route("/")
@roles_required("admin", "pastoral")
def listar():
    status = request.args.get(
        "status",
        "ativos"
    )

    consulta = db.select(PedidoOracao)

    if status == "ativos":
        consulta = consulta.where(
            PedidoOracao.status == "ativo"
        )

    elif status == "encerrados":
        consulta = consulta.where(
            PedidoOracao.status == "encerrado"
        )

    pedidos = db.session.execute(
        consulta.order_by(
            PedidoOracao.data_pedido.desc()
        )
    ).scalars().all()

    return render_template(
        "pedidos_oracao/lista.html",
        pedidos=pedidos,
        status=status
    )


@pedidos_oracao_bp.route(
    "/novo",
    methods=["GET", "POST"]
)
@roles_required("admin", "pastoral")
def criar():
    form = PedidoOracaoForm()

    configurar_choices(form)

    pessoa_id = request.args.get(
        "pessoa_id",
        type=int
    )

    if request.method == "GET":
        form.responsavel_id.data = current_user.id

        if pessoa_id:
            form.pessoa_id.data = pessoa_id

    if form.validate_on_submit():

        pedido = PedidoOracao(
            motivo=form.motivo.data.strip(),
            pessoa_id=(
                form.pessoa_id.data
                if form.pessoa_id.data != 0
                else None
            ),
            responsavel_id=(
                form.responsavel_id.data
                if form.responsavel_id.data != 0
                else None
            ),
            data_pedido=form.data_pedido.data,
            observacao=(
                form.observacao.data.strip()
                if form.observacao.data
                else None
            ),
            status="ativo"
        )

        db.session.add(pedido)
        db.session.commit()

        flash(
            "Pedido de oração registrado.",
            "success"
        )

        return redirect(
            url_for(
                "pedidos_oracao.detalhe",
                pedido_id=pedido.id
            )
        )

    return render_template(
        "pedidos_oracao/formulario.html",
        form=form,
        titulo="Novo pedido de oração"
    )


@pedidos_oracao_bp.route(
    "/<int:pedido_id>"
)
@roles_required("admin", "pastoral")
def detalhe(pedido_id):
    pedido = db.get_or_404(
        PedidoOracao,
        pedido_id
    )

    form_encerrar = EncerrarPedidoOracaoForm()
    form_reabrir = ReabrirPedidoOracaoForm()

    return render_template(
        "pedidos_oracao/detalhe.html",
        pedido=pedido,
        form_encerrar=form_encerrar,
        form_reabrir=form_reabrir
    )


@pedidos_oracao_bp.route(
    "/<int:pedido_id>/editar",
    methods=["GET", "POST"]
)
@roles_required("admin", "pastoral")
def editar(pedido_id):
    pedido = db.get_or_404(
        PedidoOracao,
        pedido_id
    )

    if pedido.status == "encerrado":
        flash(
            "Reabra o pedido antes de editá-lo.",
            "error"
        )

        return redirect(
            url_for(
                "pedidos_oracao.detalhe",
                pedido_id=pedido.id
            )
        )

    form = PedidoOracaoForm(
        obj=pedido
    )

    configurar_choices(form)

    if not form.is_submitted():
        form.pessoa_id.data = (
            pedido.pessoa_id or 0
        )

        form.responsavel_id.data = (
            pedido.responsavel_id or 0
        )

    if form.validate_on_submit():

        pedido.motivo = (
            form.motivo.data.strip()
        )

        pedido.pessoa_id = (
            form.pessoa_id.data
            if form.pessoa_id.data != 0
            else None
        )

        pedido.responsavel_id = (
            form.responsavel_id.data
            if form.responsavel_id.data != 0
            else None
        )

        pedido.data_pedido = (
            form.data_pedido.data
        )

        pedido.observacao = (
            form.observacao.data.strip()
            if form.observacao.data
            else None
        )

        db.session.commit()

        flash(
            "Pedido de oração atualizado.",
            "success"
        )

        return redirect(
            url_for(
                "pedidos_oracao.detalhe",
                pedido_id=pedido.id
            )
        )

    return render_template(
        "pedidos_oracao/formulario.html",
        form=form,
        titulo="Editar pedido de oração",
        pedido=pedido
    )


@pedidos_oracao_bp.route(
    "/<int:pedido_id>/encerrar",
    methods=["POST"]
)
@roles_required("admin", "pastoral")
def encerrar(pedido_id):
    pedido = db.get_or_404(
        PedidoOracao,
        pedido_id
    )

    form = EncerrarPedidoOracaoForm()

    if form.validate_on_submit():
        pedido.status = "encerrado"
        pedido.data_encerramento = date.today()

        db.session.commit()

        flash(
            "Pedido de oração encerrado.",
            "success"
        )

    return redirect(
        url_for(
            "pedidos_oracao.detalhe",
            pedido_id=pedido.id
        )
    )


@pedidos_oracao_bp.route(
    "/<int:pedido_id>/reabrir",
    methods=["POST"]
)
@roles_required("admin", "pastoral")
def reabrir(pedido_id):
    pedido = db.get_or_404(
        PedidoOracao,
        pedido_id
    )

    form = ReabrirPedidoOracaoForm()

    if form.validate_on_submit():
        pedido.status = "ativo"
        pedido.data_encerramento = None

        db.session.commit()

        flash(
            "Pedido de oração reaberto.",
            "success"
        )

    return redirect(
        url_for(
            "pedidos_oracao.detalhe",
            pedido_id=pedido.id
        )
    )