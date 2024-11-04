import requests

from climax import iTOKEN

iURL_DELETE = "http://apiadvisor.climatempo.com.br/api-manager/user-token/" + str(iTOKEN) + "/locales"

# Pergunta o nome da cidade
def delete_locale(iNEWCITY):
    payload = f"localeId[]={iNEWCITY}"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.request("DELETE", iURL_DELETE, headers=headers, data=payload)
    return response

if __name__ == "__main__":
    # Passo 1: Deletar a localidade existente
    locale_id_to_delete = input("Informe o ID da cidade que deseja deletar: ")
    delete_response = delete_locale(locale_id_to_delete)

    if delete_response.status_code == 200:
        print("Localidade deletada com sucesso!")
    else:
        print("Erro ao deletar localidade:", delete_response.status_code, delete_response.text)