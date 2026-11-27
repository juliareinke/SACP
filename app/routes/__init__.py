from datetime import date
from flask import Blueprint, abort, render_template
from flask_login import current_user, login_required
from sqlalchemy import func, or_
from app import db
from app.models import Acompanhamento, Pessoa, Tarefa
from app.permissions import filtrar_por_responsavel


main_bp = Blueprint("main", __name__)


def contar_visiveis(modelo, *condicoes):
    consulta = db.select(func.count()).select_from(modelo).where(*condicoes)
    return db.session.scalar(filtrar_por_responsavel(consulta, modelo)) or 0


@main_bp.route("/")
@login_required
def index():
    hoje = date.today()

    if current_user.perfil == "recepcao":
        visitantes_recentes = db.session.execute(
            db.select(Pessoa)
            .where(
                Pessoa.ativo.is_(True),
                Pessoa.situacao_igreja == "visitante",
            )
            .order_by(Pessoa.data_cadastro.desc())
            .limit(5)
        ).scalars().all()

        total_pessoas = db.session.scalar(
            db.select(func.count())
            .select_from(Pessoa)
            .where(Pessoa.ativo.is_(True))
        ) or 0
        total_visitantes = db.session.scalar(
            db.select(func.count())
            .select_from(Pessoa)
            .where(
                Pessoa.ativo.is_(True),
                Pessoa.situacao_igreja == "visitante",
            )
        ) or 0

        return render_template(
            "recepcao/index.html",
            visitantes_recentes=visitantes_recentes,
            total_pessoas=total_pessoas,
            total_visitantes=total_visitantes,
        )

    if current_user.perfil not in ("admin", "pastoral", "lider"):
        abort(403)

    acompanhamentos_ativos = contar_visiveis(
        Acompanhamento, Acompanhamento.status == "ativo"
    )
    tarefas_pendentes = contar_visiveis(Tarefa, Tarefa.status == "pendente")
    tarefas_atrasadas = contar_visiveis(
        Tarefa, Tarefa.status == "pendente", Tarefa.prazo < hoje
    )
    acompanhamentos_sem_responsavel = (
        contar_visiveis(
            Acompanhamento,
            Acompanhamento.status == "ativo",
            Acompanhamento.responsavel_id.is_(None),
        )
        if current_user.perfil in ("admin", "pastoral") else 0
    )

    proximas_tarefas = db.session.execute(
        filtrar_por_responsavel(
            db.select(Tarefa).where(Tarefa.status == "pendente")
            .order_by(Tarefa.prazo.asc()).limit(5),
            Tarefa,
        )
    ).scalars().all()

    acompanhamentos_recentes = db.session.execute(
        filtrar_por_responsavel(
            db.select(Acompanhamento)
            .where(Acompanhamento.status == "ativo")
            .order_by(Acompanhamento.data_inicio.desc()).limit(5),
            Acompanhamento,
        )
    ).scalars().all()

    visitantes_recentes = db.session.execute(
        db.select(Pessoa)
        .where(
            Pessoa.ativo.is_(True),
            Pessoa.situacao_igreja == "visitante",
        )
        .order_by(Pessoa.data_cadastro.desc())
        .limit(5)
    ).scalars().all()

    tarefas_atencao = db.session.execute(
        filtrar_por_responsavel(
            db.select(Tarefa)
            .where(
                Tarefa.status == "pendente",
                or_(
                    Tarefa.prazo < hoje,
                    Tarefa.prioridade.in_(["alta", "urgente"]),
                ),
            )
            .order_by(Tarefa.prazo.asc()).limit(5),
            Tarefa,
        )
    ).scalars().all()

    acompanhamentos_atencao = db.session.execute(
        filtrar_por_responsavel(
            db.select(Acompanhamento)
            .where(
                Acompanhamento.status == "ativo",
                or_(
                    Acompanhamento.responsavel_id.is_(None),
                    Acompanhamento.prioridade.in_(["alta", "urgente"]),
                ),
            )
            .order_by(Acompanhamento.data_inicio.desc()).limit(5),
            Acompanhamento,
        )
    ).scalars().all()

    return render_template(
        "index.html",
        hoje=hoje,
        acompanhamentos_ativos=acompanhamentos_ativos,
        tarefas_pendentes=tarefas_pendentes,
        tarefas_atrasadas=tarefas_atrasadas,
        acompanhamentos_sem_responsavel=acompanhamentos_sem_responsavel,
        proximas_tarefas=proximas_tarefas,
        acompanhamentos_recentes=acompanhamentos_recentes,
        visitantes_recentes=visitantes_recentes,
        tarefas_atencao=tarefas_atencao,
        acompanhamentos_atencao=acompanhamentos_atencao,
    )
