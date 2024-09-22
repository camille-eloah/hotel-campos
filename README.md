# hotel-campos
Sistema de administração para hotéis

## Instruções
1. Instale as bibliotecas e dependências necessárias através do requirements.txt (recomenda-se que utilize um ambiente virtual)
```
pip install -r requirements.txt
```

2. Crie as tabelas do init_db.sql no seu servidor MySQL
3. Insira o administrador executando o insert_admin.py
```
python insert_admin.py
```
   > Usuário default: admin
   
   > Senha default: 123

4. Dentro da pasta, execute o comando para rodar o servidor flask localmente
```
flask run --debug
```
