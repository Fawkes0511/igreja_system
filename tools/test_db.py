import sys
sys.path.insert(0, '.')

from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    print("=== TESTANDO CONEXÃO COM BANCO ===")
    
    try:
        # Testar conexão simples
        result = db.session.execute("SELECT version()")
        db_version = result.fetchone()
        print(f"✓ Conectado ao PostgreSQL: {db_version[0]}")
        
        # Verificar tabelas
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n✓ Tabelas encontradas: {len(tables)}")
        for table in sorted(tables):
            print(f"  - {table}")
            
    except Exception as e:
        print(f"✗ Erro na conexão: {e}")
        print("\nVerificando configuração...")
        print(f"SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
