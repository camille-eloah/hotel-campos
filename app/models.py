
from flask_login import UserMixin
import smtplib
import email.message

class User(UserMixin):
    def __init__(self, user_id, user_nome, user_email, user_senha, user_admin):
        self.id = user_id
        self.user_nome = user_nome
        self.user_email = user_email
        self.user_senha = user_senha
        self.user_admin = user_admin  

    @staticmethod
    def get(user_id):
        from app import get_db_connection
        
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM tb_usuarios WHERE user_id = %s', (user_id,))
            usuario = cursor.fetchone()
            if usuario:
                return User(usuario['user_id'], usuario['user_nome'], usuario['user_email'], usuario['user_senha'], usuario['user_admin'])
        return None

    @staticmethod
    def enviar_email(corpo, assunto, destinatario):
            
        corpo_email = corpo

        msg = email.message.Message()
        msg["Subject"] = assunto
        msg["From"] = "hotelcampus.sistema@gmail.com"
        msg["To"] = destinatario
        password = "ntzknkxmyndishta" #mjdiinyyrzelbicy
        msg.add_header("Content-Type", "text/html")
        msg.set_payload(corpo_email)

        s = smtplib.SMTP("smtp.gmail.com: 587")
        s.starttls()
        s.login(msg["From"], password)
        s.sendmail(msg["From"], [msg["To"]], msg.as_string().encode("utf-8"))