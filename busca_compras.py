import requests
from datetime import datetime
from time import sleep
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import logging
load_dotenv()

from_address = "sms.matheus.mercadao@gmail.com"
to_address = " matheusjmonteiro@hotmail.com"
NUMERO_DE_NOTIFICACOES = 3

if not os.path.exists("./logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename=f"./logs/log-{datetime.now().strftime('%d-%m-%Y')}.csv",
    filemode="a",
    format="%(asctime)s; %(msecs)d; %(levelname)s; %(message)s;",
    level=logging.DEBUG
)


def existem_novas_ordens(ordens, historico):
    """
    Função para verificar se existem ordens novas não notificadas
    :param ordens: Lista com as ordens
    :param historico: Histórico de ordens notificadas
    :return: Verdadeiro se existem ordens que não foram notificadas
    """
    for ordem in ordens:
        if ordem_eh_nova(ordem, historico):
           return True
    return False


def ordem_eh_nova(ordem, historico):
    """
    Checa se uma ordem é nova
    :param ordem: Ordem a ser verificada
    :param historico: histórico de ordens existentes
    :return: Retorna True se a ordem for nova.
    """
    return len([i for i in historico if i == ordem.get("pickingLocationName")]) <= NUMERO_DE_NOTIFICACOES

def main():
    logging.info("Iniciando o programa")
    keyToken = os.getenv("TOKEN", "")
    username = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    logging.info(f"Dados adquiridos: ")
    logging.info(f" ketToken: {keyToken},")
    logging.info(f" username: {username},")
    logging.info(f" password: {password}")
    ordens_informadas = []

    while True:
        sleep(7)
        data = datetime.now()
        url = ("https://admin.mercadao.pt/api/shoppers/orders/"
               f"available?deliveryFrom={data.strftime('%Y-%m-%d')}"
               "T00:00:00.000Z&limit=10")
        headers = {
            "Authorization": keyToken
        }
        req = None
        try:
            logging.info("Before Request")
            logging.debug(f"url: {url}")
            req = requests.get(url, headers=headers)
            logging.debug(f"After request - StatusCode: {req.status_code}")
        except ValueError as e:
            print(f"Erro ao requisitar")
            logging.error(f"Error: {e}, StatusCode: {req.status_code}")
            sleep(3)
            continue

        logging.info(f"Retorno Requisição: {req.status_code}, {req.text}")
        if req.status_code == 429:
            logging.error("Requisição com muitas tentativas")
            print("Muitas tentativas, aguardando 2 Minutos")
            sleep(120)
            continue

        if req.status_code == 401:
            print("Falha de autenticação: Renovar o Token")
            logging.error("Requisição com falha de autenticação")
            break

        ordens = req.json()
        ordens = ordens.get("orders")
        logging.debug(f"Ordems encontradas: {ordens}")
        if ordens is None or not existem_novas_ordens(ordens, ordens_informadas):
            print(f"Sem ordens, {data.strftime('%H:%M:%S')}")
            continue

        logging.info("Inicio do envio de ordens")
        for ordem in ordens:
            if not ordem_eh_nova(ordem, ordens_informadas):
                logging.info(f"Já foi enviado {NUMERO_DE_NOTIFICACOES} notificações "
                             f"para o pedido: {ordem.get('pickingLocationName')}")
                continue

            ordens_informadas.append(ordem.get("pickingLocationName"))
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Compra em espera"
            msg['From'] = from_address
            msg['X-Priority'] = '2'
            msg['To'] = to_address
            logging.debug("Criado contexto de envio de e-mails")
            # Create the message (HTML).
            html = f"""
            Existe uma compra em espera com o nome {ordem["pickingLocationName"]}
            """

            part1 = MIMEText(html, 'html')

            msg.attach(part1)
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.ehlo()
                server.starttls()
                server.login(username, password)
                server.sendmail(from_address, to_address, msg.as_string())
                server.quit()

            except ValueError as e:
                print("Erro no envio de e-mails")
                logging.error("Erro no envio do e-mail.")
                logging.error(e)
            print(f"Email Enviado, {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    print("Iniciando...")
    main()
