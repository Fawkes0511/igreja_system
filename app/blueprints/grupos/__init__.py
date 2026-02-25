from flask import Blueprint

grupos_bp = Blueprint(
    'grupos',
    __name__,
    template_folder='../../templates/main'
)

from . import routes
