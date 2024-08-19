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

from functions import auth, find_id_by_title, find_uuid_by_title, get_contents, register_with_contents, enroll, enroll_group, enroll_tenant, identify, inactivate, reset_password, revoke_all, get_enrollments, identify_users_enrollments

if input_data['action'] == 'update':
    try:
        print(f"Operação a ser realizada: {input_data['action']}")
        token = auth()
        print(f"Autenticação realizada. Token gerado: {token}")
        email = input_data['email_update']
        print(f"E-mail a ser atualizado: {email}")
        conteudos_selecionados = input_data['contents_update'].split(",")
        conteudos_selecionados = [i.strip() for i in conteudos_selecionados]
        print(f"Conteúdos selecionados para serem matriculados: {conteudos_selecionados}")
        conteudos = get_contents(token)
        member_id = identify(email)
        print(f"ID do membro {email}: {member_id}")
        status_enroll = enroll(member_id, conteudos=conteudos, conteudos_selecionados=conteudos_selecionados, token=token)
        print(f"Resposta da matricula: {status_enroll}")
    except KeyError as e:
        print(e)

elif input_data['action'] == 'create':
    try:
        print(f"Operação a ser realizada: {input_data['action']}")
        token = auth()
        print(f"Autenticação realizada. Token gerado: {token}")
        nome = input_data['name']
        group_id = input_data['group_id']
        tenant_uuid = input_data['tenant_uuid']
        email = input_data['email_create']
        print(f"Dados a serem preenchidos: /n nome: {nome}; /n email: {email}, /n turma: {group_id}, /n plataforma: {tenant_uuid}")
        conteudos = get_contents(token)
        conteudos_selecionados = input_data['contents_create'].split(",")
        conteudos_selecionados = [i.strip() for i in conteudos_selecionados]
        print(f"Conteúdos selecionados: {conteudos_selecionados}")
        member_id = register_with_contents(token=token,
                                           name=nome,
                                           email=email,
                                           conteudos_selecionados=conteudos_selecionados,
                                           conteudos=conteudos)
        print(f"Resposta do register_with_contents: {member_id}")
        response_enroll_group = enroll_group(token, member_id, group_id)
        print(f"Resposta do enroll_group: {response_enroll_group}")
        response_enroll_tenant = enroll_tenant(token, member_id, tenant_uuid)
        print(f"Resposta do enroll_group: {response_enroll_tenant}")

    except KeyError as e:
        print(e)

elif input_data['action'] == 'delete':
    try:
        print(f"Operação a ser realizada: {input_data['action']}")
        token = auth()
        print(f"Autenticação realizada. Token gerado: {token}")
        email = input_data['email_delete']
        print(f"Email a ser desativado: {email}")
        response_inactivate = inactivate(email, token)
        print(f"Resposta ação {input_data['action']}: {response_inactivate}")

    except KeyError as e:
        print(e)

elif input_data['action'] == 'revoke_all':
    try:
        print(f"Operação a ser realizada {input_data['action']}. \n 0/3 etapas concluídas.")
        token = auth()
        email = input_data['email_revoke_all']
        conteudos_selecionados = input_data['contents_to_revoke']#.split(",") # esta e a próxima linha precisam ser descomentadas para funcionar corretamente no Zapier
        # conteudos_selecionados = [i.strip() for i in conteudos_selecionados]
        conteudos = get_contents(token)
        member_id = identify(email)
        print(f"Email existente: {email}. Identificador: {member_id}. \n 1/3 etapas concluídas")
        enrollments = get_enrollments(token)
        content_ids = find_id_by_title(conteudos, conteudos_selecionados)
        member_enrollments = identify_users_enrollments(enrollments, member_id=member_id, content_ids=content_ids)
        print(f"Matrículas identificadas: {member_enrollments} \n 2/3 etapas concluídas")
        revoked_contents = revoke_all(enrollments=member_enrollments, token=token)
        print(f"Os conteúdos: \n {conteudos_selecionados} \n foram bloqueados para o aluno {email} identificador {member_id} \n 3/3 etapas concluídas")
    except KeyError as e:
        print(e)

elif input_data['action'] == 'reset_password':
    try:
        print(f"Operação a ser realizada: {input_data['action']}")
        token = auth()
        print(f"Autenticação realizada. Token gerado: {token}")
        email = input_data['email_reset_pwd']
        print(f"Email que receberá link para resetar a senha: {email}")
        response_reset_pwd = reset_password(email, token)
        print(f"Resposta ação {input_data['action']}: {response_reset_pwd}")
    except KeyError as e:
        print(e)