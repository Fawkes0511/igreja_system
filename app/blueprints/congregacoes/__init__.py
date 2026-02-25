from flask import Blueprint

congregacoes_bp = Blueprint(
    'congregacoes',
    __name__,
    template_folder='../../templates/main'
)

from . import routes
