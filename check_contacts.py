import requests
import time
from random import randint
client_id = ''
client_secret = ''
redirect_uri = ""
secret_code =''
access_token = ''
refresh_token = ''
subdomain=''
def init_oauth2():
    global access_token, refresh_token
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": secret_code,
        "redirect_uri": redirect_uri
    }

    response = requests.post(f"https://{subdomain}/oauth2/access_token", json=data).json()

    access_token = response['access_token']

    refresh_token = response["refresh_token"]

def get_list():
    global access_token
    access_token = "Bearer " + access_token
    headers = {"Authorization": access_token}
    i=0
    list_name=["Клиент", "Дорогой клиент", "Любимый клиент", "Уважаемый клиент","Бесценный клиент"]
    c=0
    while True:
        try:
            response = requests.get(f"https://{subdomain}/api/v4/contacts", headers=headers, params={'page':i}).json()
            i+=1
            k=0

            while True:
                try:
                    if response['_embedded']['contacts'][k]['name']=="" or response['_embedded']['contacts'][k]['name']=="Клиент":
                        print(response['_embedded']['contacts'][k]['name'])
                        id=response['_embedded']['contacts'][k]['id']
                        data={
                            "with" : "leads"    
                            }
                        response_contact = requests.get(f"https://{subdomain}/api/v4/contacts/{id}", headers=headers, params=data).json()
                        summ=0
                        for j in range(len(response_contact['_embedded']['leads'])):
                            resp=response_contact['_embedded']['leads'][j]['id']
                            response1=requests.get(f"https://{subdomain}/api/v4/leads/{resp}", headers=headers).json()
                            if (response1['status_id'])==142:
                                summ+=response1['price']
                        if summ<=10000:
                            data={
                                "name" : list_name[0]
                                }
                        elif summ<=35000:
                            data={
                                "name" : list_name[1]
                                }
                        elif summ<=70000:
                            data={
                                "name" : list_name[2]
                                }
                        elif summ<=100000:
                            data={
                                "name" : list_name[3]
                                }
                        else:
                            data={
                                "name" : list_name[4]
                                }
                            
                        change=(requests.patch(f"https://{subdomain}/api/v4/contacts/{id}", headers=headers, json=data))
                        print(id, change)
                        c+=1
                    k+=1
                except Exception as e:
                    break
            i+=1
        except Exception as e:
            print(i)
            break

get_list()
