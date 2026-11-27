from functools import wraps
from flask import abort
from flask_login import current_user, login_required


def roles_required(*roles):
    def decorator(view_function):
        @wraps(view_function)
        @login_required
        def wrapped_view(*args, **kwargs):
            if current_user.perfil not in roles:
                abort(403)
            return view_function(*args, **kwargs)
        return wrapped_view
    return decorator


def filtrar_por_responsavel(consulta, modelo):
    """Restringe Acompanhamento/Tarefa ao usuário líder atual."""
    if current_user.perfil == "lider":
        return consulta.where(modelo.responsavel_id == current_user.id)
    return consulta


def exigir_responsavel(registro):
    """Impede que líderes abram por ID registros de outros responsáveis."""
    if (
        current_user.perfil == "lider"
        and registro.responsavel_id != current_user.id
    ):
        abort(403)
