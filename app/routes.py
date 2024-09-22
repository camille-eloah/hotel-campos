from flask import render_template, request, redirect
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from app import app, get_db_connection, routes
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message

import smtplib
import email.message

from app.models import User

import json

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/logout')
@login_required  # Certifica-se de que o usuário está logado
def logout():
    logout_user() 
    return render_template('index.html')

@app.route('/cadastro_func')
@login_required 
def cadastro_func():
    if not current_user.user_admin:  # Verifica se user_admin não é 1
        return render_template('index.html')  # Redireciona para a página inicial se não for admin
    
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM tb_usuarios')
        usuarios = cursor.fetchall()
    connection.close()

    return render_template('cadastro_func.html', usuarios=usuarios)

@app.route('/editar_func/<string:user_nome>', methods=['POST', 'GET']) 
def editar_func(user_nome):
    connection = get_db_connection()
    
    if request.method == 'POST':
        novo_nome = request.form['user_nome']
        user_email = request.form['user_email']  
        user_senha = request.form['user_senha']

        hashed_senha = generate_password_hash(user_senha)

        with connection.cursor() as cursor:
            cursor.execute('UPDATE tb_usuarios SET user_nome = %s, user_email = %s, user_senha = %s WHERE user_nome = %s', 
                           (novo_nome, user_email, hashed_senha, user_nome))
            connection.commit()
        
        return redirect('/cadastro_func')

    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM tb_usuarios WHERE user_nome = %s', (user_nome,))
        usuario = cursor.fetchone()
    
    print("Usuário:", usuario)

    connection.close()

    return render_template('editar_func.html', usuario=usuario)


@app.route('/remove_func/<string:user_nome>', methods=['GET', 'POST'])
def remove_func(user_nome):
    connection = get_db_connection()
    
    with connection.cursor() as cursor:
        cursor.execute('SELECT user_admin FROM tb_usuarios WHERE user_nome = %s', (user_nome,))
        usuario = cursor.fetchone()

        if usuario and usuario['user_admin'] == 1:
            # Se o usuário for super administrador, não permite a remoção
            cursor.execute('SELECT * FROM tb_usuarios')
            usuarios = cursor.fetchall()
            connection.close()
            return render_template('cadastro_func.html', usuarios=usuarios, mensagem="Não é possível remover um super-administrador.")
        
        cursor.execute('DELETE FROM tb_usuarios WHERE user_nome = %s', (user_nome,))
        connection.commit()

        cursor.execute('SELECT * FROM tb_usuarios')
        usuarios = cursor.fetchall()

    connection.close()
    return render_template('cadastro_func.html', usuarios=usuarios)


@app.route('/cadastro_hosp', methods = ['POST', 'GET']) 
def cadastro_hosp():
    hospedes=[]
    connection = get_db_connection()

    with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM tb_hospedes')
            hospedes = cursor.fetchall()

    if request.method == 'POST':
        hos_nome = request.form ['nome'] 
        hos_email = request.form['email']
        hos_tlf = request.form['telefone']
        hos_cpf = request.form['cpf']
        hos_rg = request.form['rg']
        hos_pagamento = request.form['pagamento']
        hos_data_hr_out = request.form['data_hora_out']
        hos_data_hr_in = request.form['data_hora_in']
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO tb_hospedes (hos_nome, hos_email, hos_telefone, hos_cpf, hos_rg, hos_pagamento,hos_data_hora_out,hos_data_hora_in) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', (hos_nome, hos_email, hos_tlf, hos_cpf,hos_rg, hos_pagamento, hos_data_hr_out, hos_data_hr_in))
            cursor.execute('SELECT * FROM tb_hospedes')
            hospedes = cursor.fetchall()
            connection.commit()
        connection.close()

    return render_template('cadastro_hosp.html', hospedes=hospedes)

@app.route('/editar_hosp/<string:hos_nome>', methods = ['POST','GET']) # Edita os hóspedes desejados
def editar_hosp(hos_nome):
    connection = get_db_connection()
    if request.method == 'POST':
        novo_nome = request.form['hos_nome']
        hos_email = request.form ['hos_email']
        hos_telefone = request.form ['hos_telefone']
        hos_cpf = request.form ['hos_cpf']
        hos_rg = request.form ['hos_rg']
        hos_pagamento = request.form ['hos_pagamento']
        hos_data_hora_out = request.form ['hos_data_hora_out']
        hos_data_hora_in= request.form ['hos_data_hora_in']

        with connection.cursor() as cursor:
            cursor.execute('UPDATE tb_hospedes SET hos_nome = %s, hos_email = %s, hos_telefone = %s,hos_cpf= %s, hos_rg= %s, hos_pagamento = %s,hos_data_hora_out = %s, hos_data_hora_in = %s WHERE hos_nome = %s', 
                           (novo_nome, hos_email, hos_telefone, hos_cpf, hos_rg, hos_pagamento, hos_data_hora_out, hos_data_hora_in, hos_nome))
            connection.commit()
        
        return redirect('/cadastro_hosp')

    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM tb_hospedes WHERE hos_nome = %s', (hos_nome,))
        hospede = cursor.fetchone()
    
    print("Hóspede:",hospede )

    connection.close()

    return render_template('editar_hosp.html', hospede=hospede)


@app.route('/remove_hospede/<string:hos_nome>', methods=['POST', 'GET'])
def remove_hospede(hos_nome):
    connection = get_db_connection()
    mensagem = None  

    with connection.cursor() as cursor:
        try:
            cursor.execute('DELETE FROM tb_hospedes WHERE hos_nome = %s', (hos_nome,))
            connection.commit()
        except Exception:
            mensagem = "Você não pode remover esse hóspede porque provavelmente ele está com uma reserva ativa!"

        cursor.execute('SELECT * FROM tb_hospedes')
        hospedes = cursor.fetchall()

    connection.close()
    return render_template('cadastro_hosp.html', hospedes=hospedes, mensagem=mensagem)



@app.route('/cadastro_quarto', methods= ['POST', 'GET'])  
def cadastro_quarto(): 
    quartos = []
    connection = get_db_connection()

    with connection.cursor() as cursor:
        cursor.execute ('SELECT * FROM tb_quartos')
        quartos = cursor.fetchall()

    if request.method == 'POST':
        qua_numero = request.form ['numero'] 

        qua_caracteristicas = request.form.getlist('qua_caracteristicas')
        qua_caracteristicas_json = json.dumps(qua_caracteristicas)

        qua_camas = request.form['qua_camas']
        qua_valor = request.form['valor_quarto']
        
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO tb_quartos (qua_numero, qua_caracteristicas,qua_camas,qua_valor,qua_disponibilidade) VALUES (%s,%s,%s,%s,%s)', (qua_numero, qua_caracteristicas_json, qua_camas,qua_valor,'Desocupado'))
            cursor.execute ('SELECT * FROM tb_quartos')
            quartos = cursor.fetchall()
            connection.commit()
        connection.close()

    return render_template('cadastro_quarto.html', quartos=quartos)

@app.route('/editar_quarto/<string:qua_numero>', methods=['POST', 'GET']) 
def editar_quarto(qua_numero):
    connection = get_db_connection()
    
    if request.method == 'POST':
        novo_numero = request.form['qua_numero']
        qua_camas = request.form['qua_camas']
        qua_valor = request.form['qua_valor']
        
        qua_caracteristicas = request.form.getlist('qua_caracteristicas')  
        qua_caracteristicas_json = json.dumps(qua_caracteristicas)
        
        
        with connection.cursor() as cursor:
            cursor.execute('UPDATE tb_quartos SET qua_numero = %s, qua_caracteristicas = %s, qua_camas = %s, qua_valor = %s WHERE qua_numero = %s', 
                           (novo_numero, qua_caracteristicas_json, qua_camas, qua_valor, qua_numero))
            connection.commit()
        
        return redirect('/cadastro_quarto')

    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM tb_quartos WHERE qua_numero = %s', (qua_numero,))
        quarto = cursor.fetchone()
    
    print("Quarto:", quarto)

    connection.close()

    return render_template('editar_quarto.html', quarto=quarto)

@app.route('/remove_quarto/<int:qua_numero>', methods=['POST']) 
def remove_quarto(qua_numero):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM tb_quartos WHERE qua_numero = %s', (qua_numero,))
        connection.commit()

        cursor.execute('SELECT * FROM tb_quartos')
        quartos = cursor.fetchall()

    connection.close()
    return render_template('cadastro_quarto.html', quartos=quartos)

@app.route('/cadastro_hotel', methods=['POST', 'GET']) # Cadastra Hotel
def cadastro_hotel():
    hotel = []  
    connection = get_db_connection()
    
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM tb_hotel')
        hotel = cursor.fetchall()

        for h in hotel:
            print("Características antes da conversão:", h['hotel_caracteristicas'])
            h['hotel_caracteristicas'] = json.loads(h['hotel_caracteristicas'])
            print("Características após a conversão:", h['hotel_caracteristicas'])

    if request.method == 'POST':
        hotel_nome = request.form['hotel_nome']
        hotel_endereco = request.form['hotel_endereco']
        hotel_caracteristicas = request.form.getlist('hotel_caracteristicas')  
        hotel_caracteristicas_json = json.dumps(hotel_caracteristicas)
        

        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO tb_hotel (hotel_nome, hotel_endereco, hotel_caracteristicas) VALUES (%s, %s, %s)', 
                           (hotel_nome, hotel_endereco, hotel_caracteristicas_json))
            connection.commit()

            cursor.execute('SELECT * FROM tb_hotel')
            hotel = cursor.fetchall()

            print("Hotel:", hotel)
            
            for h in hotel:
                print("Características antes da conversão:", h['hotel_caracteristicas'])
                h['hotel_caracteristicas'] = json.loads(h['hotel_caracteristicas'])
                print("Características após a conversão:", h['hotel_caracteristicas'])

        connection.close()

    return render_template('cadastro_hotel.html', hotel=hotel)

@app.route('/remove_hotel/<string:hotel_nome>', methods=['GET', 'POST']) # Remove hotel desejado
def remove_hotel(hotel_nome):
    connection = get_db_connection()
    with connection.cursor() as cursor:

        cursor.execute('DELETE FROM tb_hotel WHERE hotel_nome = %s', (hotel_nome,))
        connection.commit()

        cursor.execute('SELECT * FROM tb_hotel')
        hotel = cursor.fetchall()

    connection.close()
    return render_template('cadastro_hotel.html', hotel=hotel)

        
@app.route('/editar_hotel/<string:hotel_nome>', methods=['POST', 'GET']) 
def editar_hotel(hotel_nome):
    connection = get_db_connection()
    
    if request.method == 'POST':
        novo_nome = request.form['hotel_nome']
        novo_endereco = request.form['hotel_endereco']
        hotel_caracteristicas = request.form.getlist('hotel_caracteristicas')  
        hotel_caracteristicas_json = json.dumps(hotel_caracteristicas)
        
        with connection.cursor() as cursor:
            cursor.execute('UPDATE tb_hotel SET hotel_nome = %s, hotel_endereco = %s, hotel_caracteristicas = %s WHERE hotel_nome = %s', 
                           (novo_nome, novo_endereco, hotel_caracteristicas_json, hotel_nome))
            connection.commit()
        
        return redirect('/cadastro_hotel')

    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM tb_hotel WHERE hotel_nome = %s', (hotel_nome,))
        hotel = cursor.fetchone()

    connection.close()

    return render_template('editar_hotel.html', hotel=hotel)

@app.route('/add', methods=['POST'])
def add_user():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['pass']
    

    hashed_senha = generate_password_hash(senha)
    
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO tb_usuarios (user_nome, user_email, user_senha) VALUES (%s, %s, %s)', (nome, email, hashed_senha))
        connection.commit()


        corpo = f"""
        <p style= 'color: #d63384'>Bem-vindo, {nome}!</p>
        <p>Você foi cadastrado como funcionário no Hotel Campus!</p>
        """

        assunto = f"Parabéns! Você foi cadastrado no Hotel Campus com sucesso"
        destinatario = email 

        User.enviar_email(corpo, assunto, destinatario)

    connection.close()

    return redirect('/cadastro_func')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha'] 

        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT * FROM tb_usuarios WHERE user_nome = %s', (nome,))
            usuario = cursor.fetchone()

            if usuario and check_password_hash(usuario['user_senha'], senha):
                user = User(usuario['user_id'], usuario['user_nome'], usuario['user_email'], usuario['user_senha'], usuario['user_admin'])
                login_user(user)
                print("Autenticado")
                return redirect('/')
            else:
                return "Nome de usuário ou senha inválidos."

    return render_template('login.html')



@app.route('/reservar_quarto', methods=['POST', 'GET'])
def reservar_quarto():
    quartos = []
    hospedes = []
    reservas = []

    connection = get_db_connection()
    with connection.cursor() as cursor:

        cursor.execute('SELECT * FROM tb_hospedes')
        hospedes = cursor.fetchall()

        cursor.execute('SELECT * FROM tb_quartos WHERE qua_disponibilidade = %s', ('Desocupado',))
        quartos = cursor.fetchall()

        # Buscando as reservas e realizando o JOIN entre tb_reserva_qua, tb_hospedes e tb_quartos
        cursor.execute('''
            SELECT tb_reserva_qua.res_id, tb_hospedes.hos_nome, tb_hospedes.hos_email, tb_hospedes.hos_telefone, 
                   tb_quartos.qua_numero, tb_quartos.qua_caracteristicas, tb_quartos.qua_camas, tb_quartos.qua_valor
            FROM tb_reserva_qua
            JOIN tb_hospedes ON tb_reserva_qua.res_hos_id = tb_hospedes.hos_id
            JOIN tb_quartos ON tb_reserva_qua.res_qua_id = tb_quartos.qua_id
        ''')
        reservas = cursor.fetchall()

    if request.method == 'POST':
        res_hos_id = request.form['hos_id']
        res_qua_id = request.form['qua_id']
        res_disponibilidade = request.form['disponibilidade']

        with connection.cursor() as cursor:

            cursor.execute('INSERT INTO tb_reserva_qua (res_hos_id, res_qua_id, res_disponibilidade) VALUES (%s, %s, %s)',
                           (res_hos_id, res_qua_id, res_disponibilidade))
            connection.commit()

            # UPDATE a disponibilidade do quarto para "Ocupado"
            cursor.execute('UPDATE tb_quartos SET qua_disponibilidade = %s WHERE qua_id = %s',
                           ('Ocupado', res_qua_id))
            connection.commit()

        return redirect('/reservar_quarto') 

    connection.close()

    return render_template('reservar_quarto.html', quartos=quartos, hospedes=hospedes, reservas=reservas)

@app.route('/remove_reserva/<int:res_id>', methods=['POST', 'GET'])
def remove_reserva(res_id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Buscando a reserva para obter o ID do quarto
        cursor.execute('SELECT res_qua_id FROM tb_reserva_qua WHERE res_id = %s', (res_id,))
        reserva = cursor.fetchone()

        if reserva:
            res_qua_id = reserva['res_qua_id']

            cursor.execute('DELETE FROM tb_reserva_qua WHERE res_id = %s', (res_id,))
            connection.commit()

            # UPDATE disponibilidade do quarto para "Desocupado"
            cursor.execute('UPDATE tb_quartos SET qua_disponibilidade = %s WHERE qua_id = %s',
                           ('Desocupado', res_qua_id))
            connection.commit()

    connection.close()
    return redirect('/reservar_quarto') 