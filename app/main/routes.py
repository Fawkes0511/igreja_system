from PIL import Image
import os, secrets
from datetime import datetime
from flask import redirect, url_for, render_template, request, flash, jsonify, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from app.main import main_bp
from app.models import db
from app.models.igreja import (
    Membro, Congregacao, Ministerio, Funcao, MembroMinisterio,
    Evento, Inscricao, Agenda, Presenca
)

def allowed_file(filename): return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}
def _get_attr(obj, name, default=None): return getattr(obj, name, default)
def _set_if_exists(obj, name, value):
    if hasattr(obj, name): setattr(obj, name, value)

