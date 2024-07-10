import requests
from credentials import (
    url,
    username,
    api_key,
    password,
    endpoint_contents,
    endpoint_register,
    endpoint_groups,
    endpoint_tenants,
    endpoint_enrollments,
    endpoint_inactivate
)
from input_data import input_data

# Parâmetros
url = url
api_key = api_key
username = username
password = password
endpoint_contents = endpoint_contents

headers = {
    "api_key": api_key,
    "Content-Type": "application/json"
}

def auth():
    """
    função de autenticação na api da curseduca, enviando user, password, apikey
    :return: retorna access_token
    """
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
    return access_token ##

def find_id_by_title(contents, target_titles):
    """
    função que tem o objetivo de buscar os títulos dos conteúdos selecionados no typeform para retornar o id (int)
    dos cursos na curseduca

    :param contents: recebe a lista de conteúdo resultante da função get_contents
    :param target_titles: recebe do zapier a lista de conteúdos selecionados do typeform tratados, em formato de lista de string
    :return: retorna lista de ids
    """
    contents_comma = []
    for string in target_titles:
        nova_string = string.replace("/", ",")
        contents_comma.append(nova_string)
    target_titles = contents_comma
    id_map = {item['title']: item['id'] for item in contents}
    return [id_map.get(title, None) for title in target_titles]

def find_uuid_by_title(contents, target_titles):
    """
    função que tem o objetivo de buscar os títulos dos conteúdos selecionados no typeform para retornar o uuid (string)
    dos cursos na curseduca

    :param contents: recebe a lista de conteúdo resultante da função get_contents
    :param target_titles: recebe do zapier a lista de conteúdos selecionados do typeform tratados, em formato de lista de string
    :return: retorna lista de uuids
    """
    contents_comma = []
    for string in target_titles:
        nova_string = string.replace("/", ",")
        contents_comma.append(nova_string)
    target_titles = contents_comma
    id_map = {item['title']: item['uuid'] for item in contents}
    return [id_map.get(title, None) for title in target_titles]

def get_contents(token):
    """
    tem o objetivo de retornar a lista de dicionários dos conteúdos, contendo titulo, id, uuid, slug entre outros dados
    para ser consumido pelas funções de busca de títulos
    :param token: token de acesso retornado pela função auth
    :return: retorna lista de dicionários para serem consumidos pelas funções de busca de títulos
    """

    body = {
        "username": username,
        "password": password,
    }

    headers = {
        "api_key": api_key,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # recebe resposta
    response_get = requests.get(
        endpoint_contents,
        headers=headers,
        json=body
    )

    # torna json legivel
    data = response_get.json()
    data = data['data']
    return data

def register_with_contents(token, name, email, conteudos_selecionados, conteudos):
    """
    Função que tem como objetivo fazer o fluxo principal de cadastro dos colaboradores:
    1. cadastrando o usuário na plataforma (obrigatório)
    2. concomitantemente matriculando nos conteúdos (opcional)

    :param token: token de acesso recebido na função auth
    :param name: nome que o gestor escreveu no typeform
    :param email: email que o gestor escreveu no typeform
    :param conteudos_selecionados: conteúdos selecionados pelo gestor no typeform
    :param conteudos: conteudos resultantes da função get_contents para serem buscados
    :return: retorna o user_id
    """

    content_uuids = find_uuid_by_title(conteudos, conteudos_selecionados)
    print(content_uuids)

    body = {
        "name": name,
        "email": email,
        "sendConfirmationEmail": "true",
        "contentsToEnroll": content_uuids
    }

    headers = {
        "api_key": api_key,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response_post = requests.post(endpoint_register, headers=headers, json=body)

    response_json = response_post.json()
    print(response_json)
    user_id = response_json['id']
    print(user_id)
    return user_id

def enroll_group(token, id, group_id):
    """
    Função que tem objetivo atribuir o usuário criado pela função register_with_contents à respectiva turma da empresa.
    :param token: token de acesso gerado pela função auth
    :param id: id do usuário gerado pela função register_with_contents
    :param group_id: group_id atribuído pelo typeform da empresa
    :return: retorna o body da chamada
    """

    body = {
        "member": {"id": id},
        "group": {"id": group_id},
    }

    headers = {
        "api_key": api_key,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response_post = requests.post(endpoint_groups, headers=headers, json=body)

    return response_post.json()

def enroll_tenant(token, id, tenant_uuid):
    """
    Função que tem objetivo atribuir o usuário criado pela função register_with_contents ao respectivo tenant da empresa.
    :param token: token de acesso gerado pela função auth
    :param id: id do usuário gerado pela função register_with_contents
    :param tenant_uuid: tenant_uuid atribuído pelo typeform da empresa
    :return: retorna o body da chamada
    """
    body = {
        "member": {"id": id},
        "tenant": {"uuid": tenant_uuid}
    }

    headers = {
        "api_key": api_key,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response_post = requests.post(endpoint_tenants, headers=headers, json=body)

    return response_post.json()

def identify(email):
    """
    Função que tem como objetivo identificar quem é o usuário que será utilizado nas ações de atribuir novos conteúdos
    a um colaborador existente e de remoção de colaborador
    :param email: email a ser identificado
    :return: id do usuário
    """
    endpoint_busca = f"https://prof.curseduca.pro/members/by?email={email}"

    response_get = requests.get(endpoint_busca, headers=headers)
    response_json = response_get.json()
    member_id = response_json['id']
    return member_id

def enroll(member_id, conteudos_selecionados, conteudos, token):
    """
    Função com o objetivo de matricular um usuário existente em um ou mais conteúdos, passando o member_id e o(s) content_id(s)
    :param member_id: id do usuário que foi buscado na função identify
    :param conteudos_selecionados: lista de conteúdos selecionados no typeform
    :param conteudos: conteudos resultantes da função get_contents para serem buscados
    :param token: token resultado da função auth
    :return: body da chamada
    """

    content_ids = find_id_by_title(conteudos, conteudos_selecionados)
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

        response_post = requests.post(endpoint_enrollments, headers=headers, json=body)

        response_json = response_post.json()
        print(response_json)
        return response_json

def inactivate(email, token):
    """
    Função que realiza a ação de remoção do usuário no typeform. muda o status na curseduca para inativo
    :param email: email escrito no typeform
    :param token: token resultado da função auth
    :return:
    """

    headers = {
        "api_key": api_key,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "member": {"entries": [email]}
    }

    response_patch = requests.patch(endpoint_inactivate, headers=headers, json=body)
    return response_patch.json()


if input_data['action'] == 'update':
    try:
        token = auth()
        email = input_data['email_update']
        print(email)
        conteudos_selecionados = input_data['contents_update'].split(",")
        conteudos_selecionados = [i.strip() for i in conteudos_selecionados]
        conteudos = get_contents(token)
        member_id = identify(email)
        print(member_id)
        enroll(member_id,
                  conteudos=conteudos,
                  conteudos_selecionados=conteudos_selecionados,
                  token=token)
    except KeyError as e:
        print(e)

elif input_data['action'] == 'create':
    try:
        token = auth()
        nome = input_data['name']
        group_id = input_data['group_id']
        tenant_uuid = input_data['tenant_uuid']
        email = input_data['email_create']
        conteudos = get_contents(token)
        conteudos_selecionados = input_data['contents_create'].split(",")
        conteudos_selecionados = [i.strip() for i in conteudos_selecionados]
        member_id = register_with_contents(token=token,
                                           name=nome,
                                           email=email,
                                           conteudos_selecionados=conteudos_selecionados,
                                           conteudos=conteudos)
        enroll_group(token, member_id, group_id)
        enroll_tenant(token, member_id, tenant_uuid)
        print(conteudos)
    except KeyError as e:
        print(e)

elif input_data['action'] == 'delete':
    try:
        token = auth()
        email = input_data['email_delete']
        inactivate(email, token)
    except KeyError as e:
        print(e)

