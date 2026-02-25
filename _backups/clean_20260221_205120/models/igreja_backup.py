from app.models import db
from datetime import datetime

class Congregacao(db.Model):
    __tablename__ = 'congregações'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    ativa = db.Column(db.Boolean, default=True)
    membros = db.relationship('Membro', backref='congregação', lazy=True)

class Membro(db.Model):
    __tablename__ = 'membros'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    foto = db.Column(db.String(200)) # Caminho da imagem
    tipo = db.Column(db.String(20), default='Adulto') # Adulto ou Criança
    ativo = db.Column(db.Boolean, default=True)
    observacoes = db.Column(db.Text)
    
    # Relacionamento com Congregação
    congregacao_id = db.Column(db.Integer, db.ForeignKey('congregações.id'), nullable=False)
    
    # Campos específicos para Adultos
    data_batismo = db.Column(db.Date)
    
    # Campos específicos para Crianças
    responsaveis = db.Column(db.String(200))
    info_medica = db.Column(db.Text) # Alergias, restrições, etc.
    
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Converte o objeto para dicionário (serializável)"""
        return {
            'id': self.id,
            'nome': self.nome,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'tipo': self.tipo,
            'congregacao_id': self.congregacao_id,
            'data_batismo': self.data_batismo.isoformat() if self.data_batismo else None,
            'responsaveis': self.responsaveis,
            'info_medica': self.info_medica,
            'observacoes': self.observacoes,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }

class Funcao(db.Model):
    __tablename__ = 'funções'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    ativa = db.Column(db.Boolean, default=True)
