from werkzeug.security import generate_password_hash
import pymysql
from app import get_db_connection

def insert_admin(nome, email, senha):
    connection = get_db_connection() 
    hashed_senha = generate_password_hash(senha)

    try:
        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO tb_usuarios (user_nome, user_email, user_senha, user_admin)
                VALUES (%s, %s, %s, %s)
            ''', (nome, email, hashed_senha, 1))
            connection.commit()
            print(f'Usuário admin "{nome}" inserido com sucesso.')
    except Exception as e:
        print(f'Ocorreu um erro: {e}')
    finally:
        connection.close()

# Inserindo super-administrador
insert_admin('admin', 'admin@gmail.com', '123')
