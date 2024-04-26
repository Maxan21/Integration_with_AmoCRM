import requests
import mysql.connector
import time
from datetime import datetime

client_id = ''
client_secret = ''
redirect_uri = ""
secret_code =''
access_token = ''
refresh_token = ''
def init_oauth2():
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
def get_number():
    global access_token, refresh_token
    access_token = "Bearer " + access_token
    headers = {"Authorization": access_token}
    i=1
    

    cnx=mysql.connector.connect(user='', password='', host='', database='')
    cursor=cnx.cursor(buffered=True)
    query=(f"SELECT * FROM Date_check;")
    cursor.execute(query)
    for last_time in cursor:
        c = last_time[0]
    while True:
        try:
            t = int(time.time())
            print(t)
            response=requests.get("https://itnw.amocrm.ru/api/v4/contacts", headers=headers, params={'filter[updated_at][from]':c, 'filter[updated_at][to]': t}).json()
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
                refresh_token = r['refresh_token']
                access_token_1 = "Bearer " + access_token
                headers = {"Authorization": access_token}
                response=requests.get("https://itnw.amocrm.ru/api/v4/contacts", headers=headers, params={'filter[updated_at][from]':c, 'filter[updated_at][to]': t}).json()
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
                                    ret=cursor.execute(query)
                                    for (id_contact, number) in cursor:
                                        c=1
                                        break
                                    if c!=1:
                                        sql=(f"INSERT INTO contacts(id_contact, number) VALUES(%s, %s);")
                                        val=(id_contact, phone)
                                        cursor.execute(sql, val)
                                        cnx.commit()
            
            
            sql=(f"UPDATE Date_check SET last_time={t};")
            cursor.execute(sql)
            cnx.commit()
            time.sleep(3000)
        except Exception as e:
            print(phone)
            print(i)
            cursor.close()
            cnx.close()
            break
init_oauth2()
get_number()
