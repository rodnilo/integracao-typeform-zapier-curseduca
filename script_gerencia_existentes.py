import requests

# Entrada de dados simulada para Zapier
input_data = {
    'email_create': 'email@terte54353rtteste.com.br',
    'tenant_uuid': '',
    'group_id': 4,
    'email_update': 't',
    'email_delete': 't',
    'contents_create': ['', '', ''],
    'contents_update': ['', '', ''],
    'action': 'update',
}



contents = {
    "NR-05 Comissão Interna de Prevenção de Acidentes (CIPA) - Grau de risco I": {
        "id": 325,
        "uuid": "e41425ef-830c-11ee-a986-169f154e14b3"
    },
    "NR-05 Comissão Interna de Prevenção de Acidentes (CIPA) - Grau de risco II": {
        "id": 399,
        "uuid": "5531b770-f341-11ee-ab1f-12c8d3237b4f"
    },
    "NR 10 - SEP": {
        "id": 359,
        "uuid": ""
    }
}

# Parâmetros
url = "https://prof.curseduca.pro/login"
api_key = "45e458d5634e8c0d3aa8d0d856dd8c0f22deb971"
username = "ekoateste@ekoaeducacao.com.br"
password = "mvG8sbMNJCzXJrs"

headers = {
    "api_key": api_key,
    "Content-Type": "application/json"
}

def autentica():
    body = {
        "username": username,
        "password": password,
    }

    headers = {
        "api_key": api_key,
        "Content-Type": "application/json"
    }

    # Autentica
    response_post = requests.post(url, headers=headers, json=body)

    # Extrai token
    response_json = response_post.json()
    access_token = response_json['accessToken']
    print(response_json)
    return access_token

def identifica(email):
    endpoint_busca = f"https://prof.curseduca.pro/members/by?email={email}"

    response_get = requests.get(endpoint_busca, headers=headers)
    response_json = response_get.json()
    member_id = response_json['id']
    return member_id

conteudos_escolhidos = ["NR-05 Comissão Interna de Prevenção de Acidentes (CIPA) - Grau de risco I",
                "NR-05 Comissão Interna de Prevenção de Acidentes (CIPA) - Grau de risco II"]

def matricula(member_id, conteudos, token):


    endpoint = "https://clas.curseduca.pro/enrollments"

    content_ids = [contents[i]['id'] for i in conteudos]
    print(content_ids)
    headers = {
        "api_key": api_key,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    for i in content_ids:
        body = {
            "member": {
                "id": member_id
            },
            "contentId": i
        }

        response_post = requests.post(endpoint, headers=headers, json=body)

        response_json = response_post.json()
        print(response_json)



# nome = str(input_data['nome'])
#email = str(input_data['email'])

#user_id = cadastra_com_conteudos(token, nome, email)

#matricula_turma(token, user_id, int(input_data['turma']))
#matricula_tenant(token, user_id, input_data['tenant'])"""

token = autentica()
print(token)
everton_id = identifica("evertonribeiro@ekoaeducacaotop.com.br")
print(everton_id)
matricula(everton_id, conteudos_escolhidos, token)
