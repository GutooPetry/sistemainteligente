import mercadopago
import streamlit as st
import mysql.connector


def conexao_db():
    return mysql.connector.connect(
        host="viaduct.proxy.rlwy.net",
        user="root",
        password="doUJUDeEIZUkkocinrlUoUgCaLmJwXiO",
        database="railway",
        port=16292
    )


def gerar_link_pagamento():
    conn = conexao_db()
    cursor = conn.cursor()
    sql = 'SELECT external_reference FROM external_reference WHERE id = (SELECT MAX(id) FROM external_reference);'
    cursor.execute(sql)
    external_reference = cursor.fetchall()[0][0] + 1

    sdk = mercadopago.SDK("TEST-1819274578996018-060921-d0e02f067d6c5d56f380d19ef3318c91-1849541513")

    preference_data = {
        'items': [

        ],
        "back_urls": {
            "success": "https://www.linkedin.com/in/gustavo-petry-64a8b7301",
            "failure": "https://www.linkedin.com/in/gustavo-petry-64a8b7301",
            "pending": "https://www.linkedin.com/in/gustavo-petry-64a8b7301",
        },
        "auto_return": "all",
        "external_reference": f'{external_reference}'
    }

    sql = 'SELECT id, nome_produto, quantidade, preco FROM carrinho;'
    cursor.execute(sql)

    for produto in cursor.fetchall():
        preference_data['items'].append({"id": produto[0], "title": produto[1], "quantity": produto[2],
                                         "currency_id": "BRL", "unit_price": float(produto[3])})

    result = sdk.preference().create(preference_data)
    payment = result["response"]
    link_iniciar_pagamento = payment["init_point"]

    sql = 'INSERT INTO pagamentos (data_inicio, identificador) VALUES (%s, %s);'
    dados = (result['response']['date_created'], external_reference)
    sql2 = 'INSERT INTO external_reference (external_reference) VALUES (%s);'
    dados2 = (external_reference,)
    cursor.execute(sql, dados)
    cursor.execute(sql2, dados2)
    conn.commit()
    print('deu boa')
    return link_iniciar_pagamento


def verifica_status():
    conn = conexao_db()
    cursor = conn.cursor()
    sql = 'SELECT identificador FROM pagamentos WHERE id = (SELECT MAX(id) FROM pagamentos);'
    cursor.execute(sql)
    identificador = cursor.fetchall()[0][0]
    sdk = mercadopago.SDK("TEST-1819274578996018-060921-d0e02f067d6c5d56f380d19ef3318c91-1849541513")

    filters = {
        "sort": "date_created",
        "criteria": "desc",
        "range": "date_created",
        "external_reference": f"{identificador}",
        "begin_date": "NOW-2HOURS",
        "end_date": "NOW"
    }

    while True:
        search_request = sdk.payment().search(filters)
        resultados = search_request['response']['results']
        if len(resultados) == 0:
            continue
        elif resultados[0]['external_reference'] == identificador and resultados[0]['status'] == "approved":
            print('Pagamento Aprovado')
            print(search_request['response'])
            return 'approved'
        elif resultados[0]['external_reference'] == identificador and resultados[0]['status'] == "rejected":
            return 'rejected'


# gerar_link_pagamento()
# verifica_status()
