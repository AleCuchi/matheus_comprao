import requests
from datetime import datetime
from time import sleep
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

from_address = "sms.matheus.mercadao@gmail.com"
to_address = " matheusjmonteiro@hotmail.com"
NUMERO_DE_NOTIFICACOES = 3


def main():
    print()
    keyToken = os.getenv("TOKEN","")

    data = datetime.now()
    url = f"https://admin.mercadao.pt/api/shoppers/orders/available?deliveryFrom={data.strftime('%Y-%m-%d')}T00:00:00.000Z&limit=10"

    ordens_informadas=[]
    while True:
        sleep(10)
        headers={
            "Authorization": keyToken
        }
        req=None
        try:
            req = requests.get(url,headers=headers)
        except ValueError  as e:
            print(f"Error: {e}, StatusCode: {req.status_code}")
            sleep(3)
        ordens = req.json()
        ordens = ordens.get("orders")
        if req.status_code == 429:
            sleep(120)
        if req.status_code >= 400:
            print("Erro : ", req.status_code)
            break
        if ordens is None or len(ordens) == 0:
            print(f"Sem ordens, {datetime.now().strftime('%H:%M:%S')}")
            continue        

        for ordem in ordens:
            
            if len([i for i in ordens_informadas if i == ordem.get("pickingLocationName")]) >= NUMERO_DE_NOTIFICACOES:
                continue
            
            ordens_informadas.append(ordem.get("pickingLocationName"))
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Compra em espera"
            msg['From'] = from_address
            msg['X-Priority'] = '2'
            msg['To'] = to_address

            # Create the message (HTML).
            html = f"""
            Existe uma compra em espera com o nome {ordem["pickingLocationName"]}
            """

            # Record the MIME type - text/html.
            part1 = MIMEText(html, 'html')

            # Attach parts into message container
            msg.attach(part1)

            # Credentials
            username = 'sms.matheus.mercadao@gmail.com'
            password = 'yxma gjpk fshd deqk'

            # Sending the email
            ## note - this smtp config worked for me, I found it googling around, you may have to tweak the # (587) to get yours to work
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.login(username, password)
            server.sendmail(from_address, to_address, msg.as_string())
            server.quit()
            print("Email Enviado")
        



if __name__ == "__main__":
    print("Iniciando...")
    main()