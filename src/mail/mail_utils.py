import os
import base64
import smtplib
import json
import logging
import sys
from cryptography.fernet import Fernet
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Logging system
logger = logging.getLogger(__name__)

MAIL_CONFIG_FILE = "emailSettings.json"

def get_fernet_key():    
    f_key = os.getenv("FERNET_KEY")
    if f_key is None:
        msg = "Environment system variable 'FERNET_KEY' not defined!"
        logger.error(msg)
        print(msg)
        return None
    else:
        if len(f_key) != 32:
            return None
        else:
            return base64.urlsafe_b64encode(bytes(f_key,"utf-8"))
    

def send_mail(body, subject_sufix = ""):
    try:

        #Get email_config
        email_config = {}
        with open(MAIL_CONFIG_FILE, "r", encoding="utf-8") as f_config:
            email_config = json.load(f_config)                 

        
        # Mail
        message = MIMEMultipart("alternative")
        
        #Subject
        subject_sufix = "" if len(subject_sufix) == 0 else (" - " + subject_sufix)
        message["Subject"] = email_config["subject"] + subject_sufix
        message["From"] = email_config["from"]
        message["To"] = ", ".join(email_config["to"]) #Aqui va como csv y no como una lista

        part = MIMEText(body, "plain")
        message.attach(part)

        smtp_server = smtplib.SMTP_SSL(email_config["smtp_server"],email_config["port"])
        smtp_server.ehlo()

        fernet = Fernet(get_fernet_key())
        password = fernet.decrypt(email_config["password"].encode("utf-8"))
        password = password.decode("utf-8")

        smtp_server.login(email_config["username"],password)
        smtp_server.sendmail(email_config["from"],email_config["to"],message.as_string())
        smtp_server.close()
        logger.info("Email sent!")
        
    except Exception as e:
        msg = 'Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e  #Para saber numero de linea que genera la excepcion
        logger.error(f"Error sending email: {msg}")
    

def setup_mail():
    
    try:

        fernet = Fernet(get_fernet_key())
        email_config = {}
        print("\nEMAIL CONFIGURATION")
        print("---------------------------")
        email_config["smtp_server"] = input("Enter smtp server address (ex: 'smtp.correo.net' ): ")
        email_config["port"] = input("Enter port number (ex: 465 ): ")
        email_config["username"] = input("Enter email account username (ex: 'neil@correo.net' ): ")    
        tmp = input("Enter email account password (ex: 'ABCD123' ): ")
        tmp = fernet.encrypt(tmp.encode(encoding="utf-8"))
        tmp = tmp.decode("utf-8")
        email_config["password"] = tmp
        email_config["from"] = input("Enter 'From' field of emails (ex: 'Addalia Services<no-reply@addalia.com>' ): ")
        tmp = input("Enter 'To' field of emails (ex1: jc@addalia.com  ex2: jc@addalia.com,john@addalia.com,paul@gmail.com ): ")
        tmp = tmp.replace(" ","").split(",")
        email_config["to"] = tmp 
        email_config["subject"] = input("Enter 'Subject' field of emails (ex: 'Informe de Proceso UpdateScannedPages' ): ")

        with open(MAIL_CONFIG_FILE, "w", encoding="utf-8") as archivo:
            json.dump(email_config, archivo, indent=4)

        print("\nGenerated file emailSettings.json with next content:\n")
        print(json.dumps(email_config, indent=4, ensure_ascii=False))


    except Exception as error:
        print(error)
        logger.error(error)

