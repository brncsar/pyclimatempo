import requests
import json

iTOKEN = "285b83f3f77172fb3628c75204dbe9a9"
iTIPOCONSULTA = 2

if iTIPOCONSULTA == 1:
    iCITY = input("Informe o nome da cidade: ")
    iURL = "http://apiadvisor.climatempo.com.br/api/v1/locale/city?name=" + str(iCITY) + "&token=" + str(iTOKEN)
    iRESPONSE = requests.get(iURL)
    iRETORNO_REQ = json.loads(iRESPONSE.text)
    for iCHAVE in iRETORNO_REQ:
        iID = iCHAVE['id']
        iNAME = iCHAVE['name']
        iSTATE = iCHAVE['state']
        iCOUNTRY = iCHAVE['country']
        print("id" + str(iID) + "iNAME:" + str(iNAME) + "iSTATE:" + str(iSTATE) + "iCOUNTRY" + str(iCOUNTRY))
    iNEWCITY = input ("Informe o ID da cidade:")   
    iURL = "http://apiadvisor.climatempo.com.br/api-manager/user-token/" + str(iTOKEN) + "/locales"
    payload = "localeId[]=" + str(iNEWCITY)
    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    print(payload,headers)
    iRESPONSE = requests.request("PUT",iURL, headers=headers, data=payload)
    print(iRESPONSE)
    

if iTIPOCONSULTA == 2:
    iURL = "http://apiadvisor.climatempo.com.br/api/v1/weather/locale/7564/current?token=" + str(iTOKEN)
    iRESPONSE = requests.request("GET", iURL)
    iRETORNO_REQ = json.loads(iRESPONSE.text)
    print(iRETORNO_REQ)

