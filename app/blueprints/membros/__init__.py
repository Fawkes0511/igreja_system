from flask import Blueprint

membros_bp = Blueprint(
    'membros',
    __name__,
    template_folder='../../templates/main'
)

from . import routes
