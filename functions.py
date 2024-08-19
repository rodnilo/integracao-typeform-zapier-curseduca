import requests
import os
from dotenv import load_dotenv, dotenv_values

username = os.getenv("username")
password = os.getenv("password")
api_key = os.getenv("api_key")
endpoint_register = os.getenv("endpoint_register")
endpoint_contents = os.getenv("endpoint_contents")
endpoint_groups = os.getenv("endpoint_groups")
endpoint_tenants = os.getenv("endpoint_tenants")
endpoint_enrollments = os.getenv("endpoint_enrollments")
endpoint_inactivate = os.getenv("endpoint_inactivate")
endpoint_identify = os.getenv("endpoint_identify")
endpoint_enrollments_report = os.getenv("endpoint_enrollments_report")
endpoint_restore_enrollments = os.getenv("endpoint_restore_enrollments")
endpoint_forgot_password = os.getenv("endpoint_forgot_password")
input_data = os.getenv("input_data")
url = os.getenv("url")

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
    return access_token


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
    user_id = response_json['id']
    if type(user_id) is int:
        return user_id
    else:
        return response_json


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

    return response_post

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

    return response_post

def identify(email):
    """
    Função que tem como objetivo identificar quem é o usuário que será utilizado nas ações de atribuir novos conteúdos
    a um colaborador existente e de remoção de colaborador
    :param email: email a ser identificado
    :return: id do usuário
    """
    endpoint_busca = endpoint_identify + f"by?email={email}"

    response_get = requests.get(endpoint_busca, headers=headers)
    response_json = response_get.json()
    member_id = response_json['id']
    if type(member_id) is int:
        return member_id
    else:
        return response_json
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
    headers = {
        "api_key": api_key,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    enrollments = []
    counter = 0
    for i in content_ids:
        body = {
            "member": {
                "id": member_id
            },
            "contentId": i
        }

        response_post = requests.post(endpoint_enrollments, headers=headers, json=body)

        response_json = response_post.json()
        if type(response_json) is int:
            enrollments.append(response_json)
        else:
            pass
        counter += 1
    if len(enrollments) == counter:
        return enrollments
    else:
        return response_json
    
def revoke_all(enrollments, token):
    """
    Função que revoga o acesso dos cursos que devem ser bloqueados ao usuário.
    :param enrollments: lista de ids dos cursos que devem ser bloqueados
    :param token: token resultado da função auth
    :return: lista de matrículas revogadas
    """

    for i in enrollments:
        endpoint = f"https://clas.curseduca.pro/enrollments/{i}"
        headers = {
            "api_key": api_key,
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
        response = requests.delete(endpoint, headers=headers)
    return enrollments

def identify_users_enrollments(enrollments, member_id, content_ids):
    """
    Função com o objetivo de identificar as matrículas dos colaboradores com base no input de enrollments, member_id e content_ids.
    :param member_id: id do usuário que foi buscado na função identify
    :param content_ids: lista de conteúdos selecionados no typeform
    :param enrollments: resultado da chamada get_enrollments que retorna todas as matrículas
    :return: lista de enrollments associada ao membro e aos conteúdos
    
    """    
    id_map = {enrollment['content']['id']: enrollment['id'] for enrollment in enrollments if enrollment['member']['id'] == member_id}
    print(id_map)
    enrollments_raw = [id_map.get(content_id) for content_id in content_ids]
    enrollments = [x for x in enrollments_raw if x is not None]
    return enrollments

def get_enrollments(token):
    """
    Função que retorna lista de dicionários com dados de matrícula
    :param token: token de acesso
    :return: lista de enrollments
    
    """    

    headers = {
        "api_key": api_key,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    body = {
        "username": username,
        "password": password,
    }

    enrollments = requests.get(
        endpoint_enrollments_report, 
        headers=headers,
        json=body
    )

    data = enrollments.json()
    data = data['data']
    return data

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

def reset_password(email, token):
    headers = {
        "api_key": api_key,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "username": email
    }

    response_post = requests.post(endpoint_forgot_password, headers=headers, json=body)
    return response_post.json()
