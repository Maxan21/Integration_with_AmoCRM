import requests
import mysql.connector
import time

def authorization(user, password, host, database):
    cnx=mysql.connector.connect(user='', password='', host='', database='')
    cursor=cnx.cursor(buffered=True)
    return cursor, cnx


def init_oauth2(client_id, client_secret, redirect_uri, secret_code, cursor, cnx):
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
    
    sql=(f"INSERT INTO Token(access_token, refresh_token) VALUES(%s, %s);")
    val=(access_token, refresh_token)
    cursor.execute(sql, val)
    cnx.commit()

    return access_token, refresh_token
    
	
def refresh(refresh_token, client_id, client_secret, redirect_uri, cursor, cnx):
    query=(f"SELECT refresh_token FROM Token;")
    cursor.execute(query)
    for token in cursor:
        refresh_token=token
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token[0],
        "redirect_uri": redirect_uri
    }
                
    r = requests.post("https://itnw.amocrm.ru/oauth2/access_token", json=data).json()
    access_token = r['access_token']
    refresh_token = r['refresh_token']
    access_token_1 = "Bearer " + access_token
    headers = {"Authorization": access_token_1}
    sql=(f"UPDATE Token SET refresh_token='{refresh_token}';")
    cursor.execute(sql)
    cnx.commit()
    return headers
    
def soc_fish(headers, cursor, cnx):
    key=''
    response=requests.get(f'https://socfishing.com/api/userget?key={key}', params={'min':int(time.time()-86400), 'max': int(time.time())}).json()
    
    for lead in response:
        c=0
        if 'phone' in lead:
            phone='+'+str(lead['phone'])
            query=(f"SELECT * FROM contacts WHERE number={phone};")
            cursor.execute(query)
            for (id_contact, number) in cursor:
                c=1
                break
            if c!=1:

                if 'email_id' in lead:
                    data=[{
                        'name' : 'socfishing',
                        'custom_fields_values' : [{
                            'field_name': 'Телефон',
                            'field_code': 'PHONE',
                            'values':[
                                {
                                    'value': str(phone)
                                    }
                                ]},
                            {
                            'field_name': 'Email',
                            'field_code': 'EMAIL',
                            'values':[
                                {
                                    'value': lead['email_id']
                                    }
                                ]
                                }
                            ]
                     
                        }]
                else:
                    data=[{
                        'name' : 'socfishing',
                        'custom_fields_values' : [{
                            'field_name': 'Телефон',
                            'field_code': 'PHONE',
                            'values':[
                                {
                                    'value': str(phone)
                                    }
                                ]}]}]
                response_contact=requests.post('https://itnw.amocrm.ru/api/v4/contacts', headers=headers, json=data).json()

                id_contact=response_contact["_embedded"]["contacts"][0]["id"]
                sql=(f"INSERT INTO contacts(id_contact, number) VALUES(%s, %s);")
                val=(id_contact, phone)
                cursor.execute(sql, val)
                cnx.commit()

                data_lead = [{
                        'name' : 'New Lead',  
                        'status_id': 16677820,
                        'pipeline_id': 806206,
                        'responsible_user_id': 1929733,
                        '_embedded': {
                            'contacts': [
                                {'id': id_contact}
                            ]
                        }
                    }]
                response_lead=requests.post('https://itnw.amocrm.ru/api/v4/leads', headers=headers, json=data_lead).json()
                
                data_task=[{
                    'responsible_user_id': 1929733,
                    'entity_id': response_lead['_embedded']['leads'][0]['id'],
                    'entity_type': 'leads',
                    'text': 'перекинуть на менеджера',
                    'complete_till': int(time.time())
                    }]
                response_task=requests.post('https://itnw.amocrm.ru/api/v4/tasks', headers=headers, json=data_task).json()
    cursor.close()
    cnx.close()



    
def get_number(access_token, refresh_token, client_id, client_secret, redirect_uri, cursor, cnx):
    access_token = "Bearer " + access_token
    headers = {"Authorization": access_token}
    query=(f"SELECT * FROM Date_check;")
    cursor.execute(query)
    for last_time in cursor:
        time_from = last_time[0]
    t = int(time.time())
    i=1
    while True:
        try:
            params={
                'filter[updated_at][from]': time_from,
                'filter[updated_at][to]': t, 
                'page':i
            }

            response = requests.get(f"https://itnw.amocrm.ru/api/v4/contacts", headers=headers, params=params).json()

            if 'title' in response and response['title']=='Unauthorized':
        		headers = refresh(refresh_token, client_id, client_secret, redirect_uri, cursor, cnx)
        		response = requests.get(f"https://itnw.amocrm.ru/api/v4/contacts", headers=headers, params=params).json()
            i+=1
            one_page_contacts=response['_embedded']['contacts']
            for k in range(len(one_page_contacts)):
                id_contact=one_page_contacts[k]['id']
                custom_value=one_page_contacts[k]['custom_fields_values']
                if custom_value!=None:
                    for find_phone in custom_value:
                        if find_phone['field_name']=='Телефон' or find_phone['field_code']=='PHONE':

                            value=find_phone['values']
                            for number in value:
                                    
                                phone_number=number['value']

                                phone_number=phone_number.replace(' ', '')
        
                                phone_number=phone_number.replace('-', '')
        
                                phone_number=phone_number.replace('(', '')

                                phone_number=phone_number.replace(')', '')
                                phone=''
                                for line in phone_number:
                                    if line in '+0123456789':
                                        phone+=line

                                if phone!='':
                                    c=0
                                    if phone[0]=="7" or phone[0]=="8":
                                        phone='+7'+phone[1:]
                                    query=(f"SELECT * FROM contacts WHERE number={phone} AND id_contact={id_contact};")
                                    cursor.execute(query)
                                    for (id_contact, number) in cursor:
                                        c=1
                                        break
                                    if c!=1:
                                        sql=(f"INSERT INTO contacts(id_contact, number) VALUES(%s, %s);")
                                        val=(id_contact, phone)
                                        cursor.execute(sql, val)
                                        cnx.commit()
                

        except Exception as e:
            sql=(f"UPDATE Date_check SET last_time={t};")
            cursor.execute(sql)
            cnx.commit()
            soc_fish(headers, cursor, cnx)
            break

cursor, cnx = authorization(user='', password='', host='', database='')
refresh_token = ''
query=(f"SELECT refresh_token FROM Token;")
cursor.execute(query)
for token_in_db in cursor:
    access_token=token_in_db[0]
    refresh_token=token_in_db[1]
if refresh_token='':
    access_token, refresh_token = init_oauth2(client_id = '', client_secret = '', redirect_uri = '', secret_code = '', cursor, cnx)

get_number(access_token, refresh_token, client_id='', client_secret='', redirect_uri='', cursor, cnx)

