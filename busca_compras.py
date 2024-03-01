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
    keyToken = os.getenv("TOKEN", "")

    username = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    ordens_informadas = []

    while True:
        sleep(10)
        data = datetime.now()
        url = ("https://admin.mercadao.pt/api/shoppers/orders/"
               f"available?deliveryFrom={data.strftime('%Y-%m-%d')}"
               "T00:00:00.000Z&limit=10")
        headers = {
            "Authorization": keyToken
        }
        req = None
        try:
            req = requests.get(url, headers=headers)
        except ValueError as e:
            print(f"Error: {e}, StatusCode: {req.status_code}")
            sleep(3)

        if req.status_code == 429:
            sleep(120)
            continue
        if req.status_code == 401:
            print("Erro : ", req.status_code)
            break
        ordens = req.json()
        ordens = ordens.get("orders")
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

            part1 = MIMEText(html, 'html')

            msg.attach(part1)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.login(username, password)
            server.sendmail(from_address, to_address, msg.as_string())
            server.quit()
            print(f"Email Enviado, {datetime.now().strftime('%H:%M:%S')}")
        

if __name__ == "__main__":
    print("Iniciando...")
    main()
