from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user
from app import db
from app.forms.pessoa import PessoaForm, InativarPessoaForm, ReativarPessoaForm
from app.models import Pessoa, Acompanhamento, Tarefa, PessoaPequenoGrupo, Discipulado, ParticipacaoEBD, PedidoOracao
from app.permissions import roles_required, filtrar_por_responsavel


pessoas_bp = Blueprint("pessoas", __name__, url_prefix="/pessoas")


def converter_tem_filhos(valor):
    if valor == "sim":
        return True
    if valor == "nao":
        return False
    return None


@pessoas_bp.route("/")
@roles_required("admin", "pastoral", "lider", "recepcao")
def listar():
    busca = request.args.get("busca", "").strip()
    situacao = request.args.get("situacao", "")
    status = request.args.get("status", "ativos")

    consulta = db.select(Pessoa)

    if busca:
        consulta = consulta.where(Pessoa.nome.ilike(f"%{busca}%"))
    if situacao:
        consulta = consulta.where(Pessoa.situacao_igreja == situacao)
    if status == "ativos":
        consulta = consulta.where(Pessoa.ativo.is_(True))
    elif status == "inativos":
        consulta = consulta.where(Pessoa.ativo.is_(False))

    pessoas = db.session.execute(consulta.order_by(Pessoa.nome)).scalars().all()

    return render_template(
        "pessoas/lista.html",
        pessoas=pessoas,
        busca=busca,
        situacao=situacao,
        status=status,
    )


@pessoas_bp.route("/nova", methods=["GET", "POST"])
@roles_required("admin", "pastoral", "lider", "recepcao")
def criar():
    form = PessoaForm()

    if form.validate_on_submit():
        pessoa = Pessoa(
            nome=form.nome.data.strip(),
            telefone=form.telefone.data.strip() if form.telefone.data else None,
            email=form.email.data.strip() if form.email.data else None,
            data_nascimento=form.data_nascimento.data,
            estado_civil=form.estado_civil.data or None,
            tem_filhos=converter_tem_filhos(form.tem_filhos.data),
            situacao_igreja=form.situacao_igreja.data,
        )
        db.session.add(pessoa)
        db.session.commit()
        flash("Pessoa cadastrada com sucesso.", "success")
        return redirect(url_for("pessoas.detalhe", pessoa_id=pessoa.id))

    return render_template("pessoas/formulario.html", form=form, titulo="Nova pessoa")


@pessoas_bp.route("/<int:pessoa_id>")
@roles_required("admin", "pastoral", "lider", "recepcao")
def detalhe(pessoa_id):
    pessoa = db.get_or_404(Pessoa, pessoa_id)

    inativar_form = InativarPessoaForm()
    reativar_form = ReativarPessoaForm()
    
    acompanhamentos_visiveis = []
    tarefas_visiveis = []
    vinculo_pg = None
    discipulado_ativo = None
    participacao_ebd = None
    pedidos_oracao_ativos = []

    if current_user.perfil in ("admin", "pastoral", "lider"):
        acompanhamentos_visiveis = db.session.execute(
            filtrar_por_responsavel(
                db.select(Acompanhamento)
                .where(Acompanhamento.pessoa_id == pessoa.id)
                .order_by(Acompanhamento.data_inicio.desc()),
                Acompanhamento,
            )
        ).scalars().all()

        tarefas_visiveis = db.session.execute(
            filtrar_por_responsavel(
                db.select(Tarefa)
                .where(Tarefa.pessoa_id == pessoa.id, Tarefa.status == "pendente")
                .order_by(Tarefa.prazo.asc()),
                Tarefa,
            )
        ).scalars().all()

        vinculo_pg = db.session.scalar(
            db.select(PessoaPequenoGrupo).where(
                PessoaPequenoGrupo.pessoa_id == pessoa.id,
                PessoaPequenoGrupo.ativo.is_(True),
            )
        )
        discipulado_ativo = db.session.scalar(
            db.select(Discipulado).where(
                Discipulado.pessoa_id == pessoa.id,
                Discipulado.status == "ativo",
            )
        )
        participacao_ebd = db.session.scalar(
            db.select(ParticipacaoEBD).where(
                ParticipacaoEBD.pessoa_id == pessoa.id,
                ParticipacaoEBD.ativo.is_(True),
            )
        )

    if current_user.perfil in ("admin", "pastoral"):
        pedidos_oracao_ativos = db.session.execute(
            db.select(PedidoOracao)
            .where(
                PedidoOracao.pessoa_id == pessoa.id,
                PedidoOracao.status == "ativo",
            )
            .order_by(PedidoOracao.data_pedido.desc())
        ).scalars().all()

    return render_template(
        "pessoas/detalhe.html",
        pessoa=pessoa,
        inativar_form=inativar_form,
        reativar_form=reativar_form,
        acompanhamentos_visiveis=acompanhamentos_visiveis,
        tarefas_visiveis=tarefas_visiveis,
        vinculo_pg=vinculo_pg,
        discipulado_ativo=discipulado_ativo,
        participacao_ebd=participacao_ebd,
        pedidos_oracao_ativos=pedidos_oracao_ativos,
        hoje=date.today(),
    )


@pessoas_bp.route("/<int:pessoa_id>/editar", methods=["GET", "POST"])
@roles_required("admin", "pastoral", "lider", "recepcao")
def editar(pessoa_id):
    pessoa = db.get_or_404(Pessoa, pessoa_id)
    form = PessoaForm()

    if request.method == "GET":
        form.nome.data = pessoa.nome
        form.telefone.data = pessoa.telefone
        form.email.data = pessoa.email
        form.data_nascimento.data = pessoa.data_nascimento
        form.estado_civil.data = pessoa.estado_civil or ""
        if pessoa.tem_filhos is True:
            form.tem_filhos.data = "sim"
        elif pessoa.tem_filhos is False:
            form.tem_filhos.data = "nao"
        else:
            form.tem_filhos.data = ""
        form.situacao_igreja.data = pessoa.situacao_igreja

    if form.validate_on_submit():
        pessoa.nome = form.nome.data.strip()
        pessoa.telefone = form.telefone.data.strip() if form.telefone.data else None
        pessoa.email = form.email.data.strip() if form.email.data else None
        pessoa.data_nascimento = form.data_nascimento.data
        pessoa.estado_civil = form.estado_civil.data or None
        pessoa.tem_filhos = converter_tem_filhos(form.tem_filhos.data)
        pessoa.situacao_igreja = form.situacao_igreja.data
        db.session.commit()
        flash("Cadastro atualizado com sucesso.", "success")
        return redirect(url_for("pessoas.detalhe", pessoa_id=pessoa.id))

    return render_template("pessoas/formulario.html", form=form, titulo="Editar pessoa")


@pessoas_bp.route("/<int:pessoa_id>/inativar", methods=["POST"])
@roles_required("admin", "pastoral")
def inativar(pessoa_id):
    pessoa = db.get_or_404(Pessoa, pessoa_id)
    form = InativarPessoaForm()
    if form.validate_on_submit():
        pessoa.ativo = False
        db.session.commit()
        flash("Pessoa inativada com sucesso.", "success")
    return redirect(url_for("pessoas.detalhe", pessoa_id=pessoa.id))


@pessoas_bp.route("/<int:pessoa_id>/reativar", methods=["POST"])
@roles_required("admin", "pastoral")
def reativar(pessoa_id):
    pessoa = db.get_or_404(Pessoa, pessoa_id)
    form = ReativarPessoaForm()
    if form.validate_on_submit():
        pessoa.ativo = True
        db.session.commit()
        flash("Pessoa reativada com sucesso.", "success")
    return redirect(url_for("pessoas.detalhe", pessoa_id=pessoa.id))
