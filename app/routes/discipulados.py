from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import Pessoa, Discipulado
from app.forms.discipulado import DiscipuladoForm, EncerrarDiscipuladoForm, ReabrirDiscipuladoForm
from app.permissions import roles_required


discipulados_bp = Blueprint(
    "discipulados",
    __name__,
    url_prefix="/discipulados"
)


def configurar_pessoas(form):
    pessoas = db.session.execute(
        db.select(Pessoa)
        .where(Pessoa.ativo.is_(True))
        .order_by(Pessoa.nome.asc())
    ).scalars().all()

    escolhas = [
        (pessoa.id, pessoa.nome)
        for pessoa in pessoas
    ]

    form.pessoa_id.choices = escolhas
    form.discipulador_id.choices = escolhas


def validar_dados(form, discipulado=None):
    valido = True

    if form.pessoa_id.data == form.discipulador_id.data:
        form.discipulador_id.errors.append(
            "A pessoa não pode ser seu próprio discipulador."
        )
        valido = False

    consulta = db.select(Discipulado).where(
        Discipulado.pessoa_id == form.pessoa_id.data,
        Discipulado.status == "ativo"
    )

    if discipulado is not None:
        consulta = consulta.where(
            Discipulado.id != discipulado.id
        )

    existente = db.session.scalar(consulta)

    if existente:
        form.pessoa_id.errors.append(
            "Esta pessoa já possui um discipulado ativo."
        )
        valido = False

    return valido


@discipulados_bp.route("/")
@roles_required("admin", "pastoral", "lider")
def listar():
    status = request.args.get(
        "status",
        "ativos"
    )

    consulta = db.select(Discipulado)

    if status == "ativos":
        consulta = consulta.where(
            Discipulado.status == "ativo"
        )

    elif status == "encerrados":
        consulta = consulta.where(
            Discipulado.status == "encerrado"
        )

    discipulados = db.session.execute(
        consulta.order_by(
            Discipulado.data_inicio.desc()
        )
    ).scalars().all()

    return render_template(
        "discipulados/lista.html",
        discipulados=discipulados,
        status=status
    )


@discipulados_bp.route(
    "/novo",
    methods=["GET", "POST"]
)
@roles_required("admin", "pastoral")
def criar():
    form = DiscipuladoForm()

    configurar_pessoas(form)

    pessoa_id = request.args.get(
        "pessoa_id",
        type=int
    )

    if (
        request.method == "GET"
        and pessoa_id
        and any(
            escolha[0] == pessoa_id
            for escolha in form.pessoa_id.choices
        )
    ):
        form.pessoa_id.data = pessoa_id

    if form.validate_on_submit():

        if validar_dados(form):

            discipulado = Discipulado(
                pessoa_id=form.pessoa_id.data,
                discipulador_id=form.discipulador_id.data,
                data_inicio=form.data_inicio.data,
                status="ativo",
                observacao=(
                    form.observacao.data.strip()
                    if form.observacao.data
                    else None
                )
            )

            db.session.add(discipulado)
            db.session.commit()

            flash(
                "Discipulado criado com sucesso.",
                "success"
            )

            return redirect(
                url_for(
                    "discipulados.detalhe",
                    discipulado_id=discipulado.id
                )
            )

    return render_template(
        "discipulados/formulario.html",
        form=form,
        titulo="Novo discipulado"
    )


@discipulados_bp.route(
    "/<int:discipulado_id>"
)
@roles_required("admin", "pastoral", "lider")
def detalhe(discipulado_id):
    discipulado = db.get_or_404(
        Discipulado,
        discipulado_id
    )

    form_encerrar = EncerrarDiscipuladoForm()
    form_reabrir = ReabrirDiscipuladoForm()

    return render_template(
        "discipulados/detalhe.html",
        discipulado=discipulado,
        form_encerrar=form_encerrar,
        form_reabrir=form_reabrir
    )


@discipulados_bp.route(
    "/<int:discipulado_id>/editar",
    methods=["GET", "POST"]
)
@roles_required("admin", "pastoral")
def editar(discipulado_id):
    discipulado = db.get_or_404(
        Discipulado,
        discipulado_id
    )

    if discipulado.status == "encerrado":
        flash(
            "Reabra o discipulado antes de editá-lo.",
            "error"
        )

        return redirect(
            url_for(
                "discipulados.detalhe",
                discipulado_id=discipulado.id
            )
        )

    form = DiscipuladoForm(
        obj=discipulado
    )

    configurar_pessoas(form)

    if form.validate_on_submit():

        if validar_dados(
            form,
            discipulado
        ):
            discipulado.pessoa_id = (
                form.pessoa_id.data
            )

            discipulado.discipulador_id = (
                form.discipulador_id.data
            )

            discipulado.data_inicio = (
                form.data_inicio.data
            )

            discipulado.observacao = (
                form.observacao.data.strip()
                if form.observacao.data
                else None
            )

            db.session.commit()

            flash(
                "Discipulado atualizado.",
                "success"
            )

            return redirect(
                url_for(
                    "discipulados.detalhe",
                    discipulado_id=discipulado.id
                )
            )

    return render_template(
        "discipulados/formulario.html",
        form=form,
        titulo="Editar discipulado",
        discipulado=discipulado
    )


@discipulados_bp.route(
    "/<int:discipulado_id>/encerrar",
    methods=["POST"]
)
@roles_required("admin", "pastoral")
def encerrar(discipulado_id):
    discipulado = db.get_or_404(
        Discipulado,
        discipulado_id
    )

    form = EncerrarDiscipuladoForm()

    if form.validate_on_submit():

        if discipulado.status == "ativo":
            discipulado.status = "encerrado"
            discipulado.data_encerramento = (
                date.today()
            )

            db.session.commit()

            flash(
                "Discipulado encerrado.",
                "success"
            )

    return redirect(
        url_for(
            "discipulados.detalhe",
            discipulado_id=discipulado.id
        )
    )


@discipulados_bp.route(
    "/<int:discipulado_id>/reabrir",
    methods=["POST"]
)
@roles_required("admin", "pastoral")
def reabrir(discipulado_id):
    discipulado = db.get_or_404(
        Discipulado,
        discipulado_id
    )

    form = ReabrirDiscipuladoForm()

    if form.validate_on_submit():

        outro_ativo = db.session.scalar(
            db.select(Discipulado)
            .where(
                Discipulado.pessoa_id == discipulado.pessoa_id,
                Discipulado.status == "ativo",
                Discipulado.id != discipulado.id
            )
        )

        if outro_ativo:
            flash(
                "Esta pessoa já possui outro discipulado ativo.",
                "error"
            )

        else:
            discipulado.status = "ativo"
            discipulado.data_encerramento = None

            db.session.commit()

            flash(
                "Discipulado reaberto.",
                "success"
            )

    return redirect(
        url_for(
            "discipulados.detalhe",
            discipulado_id=discipulado.id
        )
    )