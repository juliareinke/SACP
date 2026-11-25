import csv
import io
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from sqlalchemy import func
from app import db
from app.models import Pessoa, Acompanhamento, RegistroAcompanhamento, Tarefa
from app.permissions import roles_required


relatorios_bp = Blueprint(
    "relatorios",
    __name__,
    url_prefix="/relatorios"
)

FUSO = ZoneInfo("America/Sao_Paulo")

TIPOS_REGISTRO = [
    ("whatsapp", "WhatsApp"),
    ("ligacao", "Ligação"),
    ("visita", "Visita"),
    ("retorno", "Retorno"),
    ("encaminhamento", "Encaminhamento"),
    ("outro", "Outro"),
]


def contar(modelo, *condicoes):
    return db.session.scalar(
        db.select(func.count())
        .select_from(modelo)
        .where(*condicoes)
    ) or 0


def obter_periodo():
    hoje = datetime.now(FUSO).date()
    primeiro_dia = hoje.replace(day=1)

    inicio_texto = request.args.get(
        "inicio",
        primeiro_dia.isoformat()
    )

    fim_texto = request.args.get(
        "fim",
        hoje.isoformat()
    )

    try:
        periodo_inicio = date.fromisoformat(inicio_texto)
        periodo_fim = date.fromisoformat(fim_texto)

        if (
            periodo_inicio > periodo_fim
            or periodo_fim == date.max
        ):
            raise ValueError

        return periodo_inicio, periodo_fim

    except (ValueError, TypeError):
        return None


def gerar_dados_relatorio(periodo_inicio, periodo_fim):

    inicio_datetime = datetime.combine(
        periodo_inicio,
        time.min,
        tzinfo=FUSO
    )

    fim_datetime = datetime.combine(
        periodo_fim + timedelta(days=1),
        time.min,
        tzinfo=FUSO
    )

    indicadores = {

        "visitantes": contar(
            Pessoa,
            Pessoa.situacao_igreja == "visitante",
            Pessoa.data_cadastro >= inicio_datetime,
            Pessoa.data_cadastro < fim_datetime
        ),

        "acompanhamentos_iniciados": contar(
            Acompanhamento,
            Acompanhamento.data_inicio >= periodo_inicio,
            Acompanhamento.data_inicio <= periodo_fim
        ),

        "acompanhamentos_encerrados": contar(
            Acompanhamento,
            Acompanhamento.data_encerramento >= periodo_inicio,
            Acompanhamento.data_encerramento <= periodo_fim
        ),

        "registros": contar(
            RegistroAcompanhamento,
            RegistroAcompanhamento.data >= inicio_datetime,
            RegistroAcompanhamento.data < fim_datetime
        ),

        "visitas": contar(
            RegistroAcompanhamento,
            RegistroAcompanhamento.tipo == "visita",
            RegistroAcompanhamento.data >= inicio_datetime,
            RegistroAcompanhamento.data < fim_datetime
        ),

        "tarefas_concluidas": contar(
            Tarefa,
            Tarefa.status == "concluida",
            Tarefa.data_conclusao >= inicio_datetime,
            Tarefa.data_conclusao < fim_datetime
        )

    }

    resultados_tipos = db.session.execute(
        db.select(
            RegistroAcompanhamento.tipo,
            func.count(RegistroAcompanhamento.id)
        )
        .where(
            RegistroAcompanhamento.data >= inicio_datetime,
            RegistroAcompanhamento.data < fim_datetime
        )
        .group_by(RegistroAcompanhamento.tipo)
    ).all()

    contagens = {
        tipo: quantidade
        for tipo, quantidade in resultados_tipos
    }

    tipos_registro = [
        {
            "codigo": codigo,
            "nome": nome,
            "total": contagens.get(codigo, 0)
        }
        for codigo, nome in TIPOS_REGISTRO
    ]

    return indicadores, tipos_registro


@relatorios_bp.route("/")
@roles_required("admin", "pastoral")
def index():

    periodo = obter_periodo()

    if periodo is None:
        flash(
            "Informe um período válido.",
            "error"
        )
        return redirect(
            url_for("relatorios.index")
        )

    periodo_inicio, periodo_fim = periodo

    indicadores, tipos_registro = gerar_dados_relatorio(
        periodo_inicio,
        periodo_fim
    )

    return render_template(
        "relatorios/index.html",
        periodo_inicio=periodo_inicio,
        periodo_fim=periodo_fim,
        indicadores=indicadores,
        tipos_registro=tipos_registro
    )


@relatorios_bp.route("/exportar.csv")
@roles_required("admin", "pastoral")
def exportar():

    periodo = obter_periodo()

    if periodo is None:
        flash(
            "Informe um período válido para exportação.",
            "error"
        )
        return redirect(
            url_for("relatorios.index")
        )

    periodo_inicio, periodo_fim = periodo

    indicadores, tipos_registro = gerar_dados_relatorio(
        periodo_inicio,
        periodo_fim
    )

    arquivo = io.StringIO(newline="")

    escritor = csv.writer(
        arquivo,
        delimiter=";"
    )

    escritor.writerow([
        "SACP - Relatório Gerencial"
    ])

    escritor.writerow([
        "Período",
        (
            f"{periodo_inicio.strftime('%d/%m/%Y')} "
            f"a {periodo_fim.strftime('%d/%m/%Y')}"
        )
    ])

    escritor.writerow([])

    escritor.writerow([
        "Indicador",
        "Quantidade"
    ])

    indicadores_csv = [
        (
            "Visitantes cadastrados (situação atual: visitante)",
            indicadores["visitantes"]
        ),
        (
            "Acompanhamentos iniciados",
            indicadores["acompanhamentos_iniciados"]
        ),
        (
            "Acompanhamentos encerrados",
            indicadores["acompanhamentos_encerrados"]
        ),
        (
            "Registros de acompanhamento",
            indicadores["registros"]
        ),
        (
            "Visitas registradas",
            indicadores["visitas"]
        ),
        (
            "Tarefas concluídas",
            indicadores["tarefas_concluidas"]
        ),
    ]

    for nome, quantidade in indicadores_csv:
        escritor.writerow([
            nome,
            quantidade
        ])

    escritor.writerow([])

    escritor.writerow([
        "Registros por tipo",
        "Quantidade"
    ])

    for item in tipos_registro:
        escritor.writerow([
            item["nome"],
            item["total"]
        ])

    nome_arquivo = (
        f"sacp_relatorio_"
        f"{periodo_inicio.isoformat()}_"
        f"{periodo_fim.isoformat()}.csv"
    )

    conteudo = arquivo.getvalue().encode("utf-8-sig")

    resposta = Response(
        conteudo,
        mimetype="text/csv"
    )

    resposta.headers["Content-Disposition"] = (
        f'attachment; filename="{nome_arquivo}"'
    )

    resposta.headers["Cache-Control"] = "no-store"

    return resposta