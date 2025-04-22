import logging
import sys
import math
import time
import os
from PyPDF2 import PdfReader
from config import Config
from dms import api_dms
from helpers import parse_dms_query
from mail.mail_utils import send_mail
from datetime import datetime

# Logging system
logger = logging.getLogger(__name__)

# App Config
app_config = Config({})

def get_pdf_pages(id):

    num_pages = 0

    # Obtenemos hijos del expediente (siempre sera un solo hijo para estos tipos de exp)
    search_response = api_dms.get_document_childrens(id)
    childrens = len(search_response["docs"])
    if childrens == 0:
        msg = f"Document {id} does not have childrens (Documento o Caratula)"
        logger.warning(msg)
        return num_pages

    # Next step
    document = search_response["docs"][0]  # Podria ser Documento o Caratula
    document_id = document["#Id"]
    document_type = document["type"]

    # Next step
    # Get children (Item document) from Documento o Caratula
    search_response = api_dms.get_document_childrens(document_id)
    childrens = len(search_response["docs"])
    if childrens == 0:
        msg = f"Document (Documento o Caratula) does not have multimedia (item file) associated"
        logger.warning(msg)
        return num_pages

    # Next step
    item = search_response["docs"][0]
    item_id = item["#Id"]

    # Get PDF
    pdf_file = item_id + ".pdf"
    resp = api_dms.get_multimedia_item(item_id, pdf_file)

    if resp:
        # Get number of pages
        reader = PdfReader(pdf_file)
        num_pages = len(reader.pages)

        # Borramos el archivo PDF
        os.remove(pdf_file)
    else:
        msg = f"Cannot obtain PDF item for Document Id {id}, Document Type {document_type}, Item Id {item_id}"
        logger.error(msg)

    return num_pages


def update_document_pages(id, pages):

    data = {
        "attributes": {
            "operation_scanned_pages": str(pages)
        }
    }
    if not api_dms.update_document(id, data):
        return False
    else:
        return True

def run():
    
    found_errors = False
    msg = "Process started at " + datetime.today().strftime("%Y%m%d - %H:%M:%S")
    body_email = [msg]

    try:
        #Get DMS query from configuration
        logger.info(f"Configured query: {app_config.get_query()}")
        parsed_query = parse_dms_query(app_config.get_query())
        logger.info(f"Final query: {parsed_query}")

        body_email.append(f"Parsed query: {parsed_query}")

        #
        docs_search = api_dms.get_documents_by_query(parsed_query, None, None, None, True)

        total_docs = 0
        if not docs_search:
            msg = f"Configured query has errors. Check log file"
            #body_email.append(msg)
            #logger.error(msg)
            raise Exception(msg)
        else:
            total_docs = int(docs_search["meta"]["total"])
            if total_docs == 0:
                msg = "Executed query has not found any matching documents"
                body_email.append(msg)
                logger.info(msg)
                return
            else:
                msg = f"Total number of documents matching the query: {total_docs}"
                logger.info(msg)
                body_email.append(msg)

                #Calculate total of pages 
                total_pages = math.ceil(total_docs / app_config.get_query_pagesize())
                total_updates = 0
                for page in range(0, total_pages):
                    docs_search = api_dms.get_documents_by_query(parsed_query, None, page+1, app_config.get_query_pagesize(), False)

                    documents = docs_search["docs"]

                    for doc in documents:
                        
                        documet_id = doc["#Id"]
                        
                        pdf_pages = get_pdf_pages(documet_id)
                        msg = f"Number of pages in document {documet_id}:{pdf_pages}"
                        logger.info(msg)

                        # Update Document - Field 'operation_scanned_pages'                
                        st = update_document_pages(documet_id, pdf_pages)
                        if not st:
                            logger.error(
                                f"Could not update pages of document {documet_id}")
                        else:
                            total_updates = total_updates + 1
                            logger.info(
                                f"Document {documet_id} updated with {pdf_pages} pages")

                            msg = f"Updated documents:{total_updates}"
                            print(f"\r{msg}", end='')
                            sys.stdout.flush()

                        time.sleep(app_config.get_delay())        

                msg = f"Total documents: {total_docs} - Updated documents: {total_updates}"
                logger.info(msg)
                body_email.append(msg)

    except Exception as error:
        found_errors = True
        logger.error(error)
        body_email.append(error)    
        
    finally:        
        msg = "Process finished at " + datetime.today().strftime("%Y%m%d - %H:%M:%S")
        body_email.append(msg)

        if app_config.get_send_email():
            subject_sufix = "Errors" if found_errors else "Success"
            #Sent email
            body = "\n".join(body_email)
            send_mail(body,subject_sufix)


def start(config):
    global app_config
    app_config = config    
    st_login = None

    # DMS - Login    
    if not api_dms.login(app_config.get_dms_uri(), 
                    app_config.get_dmsuser_name() , 
                    app_config.get_dmsuser_pass(), False):    
        logger.warning("Process cannot continue")    
        return    
    
    #Main process start!
    run()

    api_dms.logout()


