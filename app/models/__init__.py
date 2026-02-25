from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importar modelos depois de definir db
from app.models.igreja import Membro, Congregacao, Ministerio, Funcao, MembroMinisterio
from app.models.usuario import Usuario

__all__ = ['db', 'Membro', 'Congregacao', 'Ministerio', 'Funcao', 
           'MembroMinisterio', 'Usuario']
