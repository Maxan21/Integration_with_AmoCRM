import requests
import time
client_id = ''
client_secret = ''
redirect_uri = ""
secret_code =''
access_token = ''
refresh_token = ''
class AmoCRMWrapper:
    def init_oauth2(self):
        global access_token, refresh_token
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "code": secret_code,
            "redirect_uri": redirect_uri
        }

        response = requests.post("https://itnw.amocrm.ru/oauth2/access_token", json=data).json()
        access_token = response['access_token']
        refresh_token = response["refresh_token"]
    def get_list(self):
        n=1
        s=''
        global access_token, refresh_token
        access_token = "Bearer " + access_token
        headers = {"Authorization": access_token}
        token = "c5645b5cc33fdec3746a1e1655741a528509f4f6"
        headers1={
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Token {token}",
        }
        
        for k in range(1, 400):
            try:
                response = requests.get("https://itnw.amocrm.ru/api/v4/companies", headers=headers, params={'page': k}).json()
                i=0
                if 'title' in response and response['title']=='Unauthorized':
                    data = {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "redirect_uri": redirect_uri
                    }
                    r = requests.post("https://itnw.amocrm.ru/oauth2/access_token", json=data).json()
                    access_token = r['access_token']
                    access_token = "Bearer " + access_token
                    headers = {"Authorization": access_token}
                    response = requests.get("https://itnw.amocrm.ru/api/v4/companies", headers=headers, params={'page': k}).json()
                while True:
                    try:
                        if {'id': 539510, 'name': 'Ликвидирована', 'color' : None} not in response['_embedded']["companies"][i]['_embedded']['tags']:
                            if  response['_embedded']["companies"][i]['custom_fields_values']!=None:
                                for custom in range(len(response['_embedded']["companies"][i]['custom_fields_values'])):
                                    if 'field_name' in response['_embedded']["companies"][i]['custom_fields_values'][custom] and response['_embedded']["companies"][i]['custom_fields_values'][custom]['field_name']=='ИНН':
                                        inn=response['_embedded']["companies"][i]['custom_fields_values'][custom]['values'][0]['value']
                                        id_company=response['_embedded']["companies"][i]["id"]
                                        data={
                                            "query": inn,
                                            "status": ["LIQUIDATING", "LIQUIDATED"]
                                        }
                                        response1=requests.post('http://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party', headers=headers1, json = data)
                                        if response1.status_code == 403:
                                            time.sleep(80000)
                                            response1=requests.post('http://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party', headers=headers1, json = data).json()

                                        if (response1.json())['suggestions'] != []:
                                            
                                            for color in response['_embedded']["companies"][i]['_embedded']['tags']:
                                                del color['color']
                                            if {'id': 539510, 'name': 'Ликвидирована'} not in response['_embedded']["companies"][i]['_embedded']['tags']:
                                                response['_embedded']["companies"][i]['_embedded']['tags'].append({'name': 'Ликвидирована'})
                                                data={
                                                    "_embedded": {
                                                    "tags": response['_embedded']["companies"][i]['_embedded']['tags']
                                                         }
                                                        
                                                        
                                                        
                                                        }
                                                p=requests.patch(f"https://itnw.amocrm.ru/api/v4/companies/{id_company}", headers=headers, json=data)
            
                    except Exception as e:
                        break
                    i+=1
            except Exception as e:
                print(response)
                break
        
        

        
    
amocrm_wrapper_1 = AmoCRMWrapper()
amocrm_wrapper_1.init_oauth2()
amocrm_wrapper_1.get_list()
