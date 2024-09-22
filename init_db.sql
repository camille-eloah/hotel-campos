CREATE DATABASE hotel_campus_db;
USE hotel_campus_db;

CREATE TABLE tb_usuarios (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_nome VARCHAR(80) NOT NULL,
    user_email VARCHAR(120) NOT NULL,
    user_senha VARCHAR(255) NOT NULL,
    user_admin TINYINT(1) NOT NULL DEFAULT 0 -- Para dizer se o usuario é superadmin ou não
);


CREATE TABLE tb_hospedes (
    hos_id INT AUTO_INCREMENT PRIMARY KEY,
    hos_nome VARCHAR(80) NOT NULL,
    hos_email VARCHAR(120) NOT NULL,
    hos_telefone INT NOT NULL, 
    hos_cpf VARCHAR(80) NOT NULL,
    hos_rg VARCHAR(80) NOT NULL,
    hos_pagamento VARCHAR(255) NOT NULL,
    hos_data_hora_out DATETIME,
    hos_data_hora_in DATETIME
);

CREATE TABLE tb_hotel (
    hotel_id INT AUTO_INCREMENT PRIMARY KEY, 
    hotel_nome VARCHAR(255) NOT NULL,
    hotel_endereco VARCHAR(255) NOT NULL, 
    hotel_caracteristicas JSON NOT NULL
);

CREATE TABLE tb_quartos(
    qua_id INT AUTO_INCREMENT PRIMARY KEY,
    qua_numero INT NOT NULL,
    qua_caracteristicas JSON NOT NULL, 
    qua_camas INT NOT NULL,
    qua_valor INT NOT NULL,
    qua_disponibilidade VARCHAR(80)  
);

CREATE TABLE tb_reserva_qua(
    res_id INT AUTO_INCREMENT PRIMARY KEY,
    res_hos_id INT,
    res_qua_id INT,
    res_disponibilidade VARCHAR(80), 
    FOREIGN KEY(res_hos_id) REFERENCES tb_hospedes(hos_id),
    FOREIGN KEY(res_qua_id) REFERENCES tb_quartos(qua_id)
);
