import logging
import requests
from io import BytesIO


# Logging system
logger = logging.getLogger(__name__)

# Dms Session After Login
session = None

# Dms API address
api_base_url = None

# API User
api_user = None

# Indicates whether you need to check if the SSL certificates are valid or not
verify_ssl = None

# Base Headers for HTTP operations
base_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
}

# Disable warning messages for urllib3 packcage
requests.packages.urllib3.disable_warnings()


def login(url, user, password, validate_ssl_certificates):
    global session
    global api_user
    api_user = user
    global api_base_url
    api_base_url = url
    global verify_ssl
    verify_ssl = validate_ssl_certificates

    endpoint = url + "/dms/authenticate"
    try:
        data_to_send = {
            "user": user,
            "pass": password
        }
        # Login process
        session = requests.Session()
        response = session.post(
            endpoint, json=data_to_send, headers=base_headers, verify=verify_ssl)
        if (response.status_code == 200):
            logger.info(f"Connected to DMS ({user})")
            return True
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Fail authenticating user {user}: {error.args}"
        logger.error(msg)
        return False


def logout():
    global api_base_url
    global api_user
    global session
    endpoint = api_base_url + "/dms/authenticate"
    try:
        # Disconnect from DMS
        response = session.delete(
            endpoint, headers=base_headers, verify=verify_ssl)
        if (response.status_code == 200):
            logger.info(f"Disconnected from DMS ({api_user})")
            # Cerramos sesion libreria request
            session.close()
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error disconnecting user {api_user}: {error.args}"
        logger.error(msg)
    finally:
        api_base_url = None
        session = None
        api_user = None


def get_dms_info():
    endpoint = api_base_url + "/dms/info"
    try:
        # Get DMS Version
        response = session.get(
            endpoint, headers=base_headers, verify=verify_ssl)
        if (response.status_code == 200):
            logger.info("Retrieved DMS Information - Done")
            return response.json()
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error getting dms info: {error.args}"
        logger.error(msg)
        return None


def get_documents_by_query(query,
                           order="$#TModificado",
                           page=None,
                           page_size=None,
                           only_meta=False):
    endpoint = api_base_url + "/dms/documents"
    custom_headers = base_headers.copy()
    try:
        custom_headers["query"] = query
        custom_headers["order"] = order
        custom_headers["deleted"] = "false"
        if (page != None) and (page_size != None):
            custom_headers["page"] = str(page)
            custom_headers["pageSize"] = str(page_size)
        if only_meta == True:
            custom_headers["onlyMeta"] = "true"

        # Search documents
        response = session.get(
            endpoint, headers=custom_headers, verify=verify_ssl)
        if (response.status_code == 200):
            result = response.json()
            msg = " - Total docs:" + \
                result["meta"]["total"] + " - Retrieved:" + \
                str(len(result["docs"]))
            logger.info(f"DMS document's search finished. Query: {query}{msg}")
            return result
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error searching documents: {error.args}"
        logger.error(msg)
        return None


def get_document_by_id(id):
    endpoint = api_base_url + "/dms/documents/" + str(id)
    try:
        response = session.get(
            endpoint, headers=base_headers, verify=verify_ssl)
        if (response.status_code == 200):
            logger.info(f"Retrieved document {id} from DMS")
            return response.json()
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error getting document {id}: {error.args}"
        logger.error(msg)
        return None


def get_document_childrens(id):
    endpoint = api_base_url + "/dms/documents/" + str(id) + "/children"
    try:
        response = session.get(
            endpoint, headers=base_headers, verify=verify_ssl)
        if (response.status_code == 200):
            logger.info(f"Retrieved childrens for document {id} from DMS")
            return response.json()
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error getting childrens for document {id}: {error.args}"
        logger.error(msg)
        return None


def update_document(id, data):
    endpoint = api_base_url + "/dms/documents/" + str(id)
    try:
        response = session.put(endpoint, json=data,
                               headers=base_headers, verify=verify_ssl)
        if (response.status_code == 200):
            logger.info(f"Updated document {id}")
            return response.json()
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error updating document {id}: {error.args}"
        logger.error(msg)
        return None


def create_document(parent_id, data):
    # parent_id => #IdAgregadoSuperior
    # Important: This endpoint only works in repositories v6.
    # Not tested
    endpoint = api_base_url + "/dms/documents/" + str(parent_id) + "/new"
    try:
        response = session.post(endpoint, json=data,
                                headers=base_headers, verify=verify_ssl)
        if (response.status_code == 200):
            result = response.json()
            new_doc_id = result["attributes"]["#Id"]
            logger.info(f"Document created {new_doc_id}")
            return result
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error creating document: {error.args}"
        logger.error(msg)
        return None


def delete_document(id):
    # Not tested
    endpoint = api_base_url + "/dms/documents/" + str(id)
    try:
        response = session.post(
            endpoint, headers=base_headers, verify=verify_ssl)
        if (response.status_code == 200):
            logger.info(f"Document {id} deleted")
            return True
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error deleteing document {id}: {error.args}"
        logger.error(msg)
        return False


def get_multimedia_item(id, output_file):
    # Optional headers
    # Mime-Type: "image/jpeg"   (e.g. Convert tiff to jpeg)
    # Verification: "TimeStamp"
    ####
    endpoint = api_base_url + "/dms/documents/" + str(id) + "/item"
    response = None
    try:
        response = session.get(
            endpoint, headers=base_headers, verify=verify_ssl, stream=True)
        if (response.status_code == 200):
            item_size = len(response.content)
            with open(output_file, "wb") as file:
                for chunk in response.iter_content(chunk_size=65536):
                    file.write(chunk)
            logger.info(
                f"Retrieved multimedia for item {id} - Size: {item_size}")
            return True
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error getting multimedia item for for document {id}: {error.args}"
        logger.error(msg)
        return None
    finally:
        # Important: Do not forget to close "response" when it's created with "stream=True" flag.
        response.close()


# Esta funcion difiere de la original get_multimedia_item en que aquella escribe el archivo en disco
# y esta lo guarda en memoria en una estructura BytesIO.
# En principio se crea esta funcion para ver si es posible obtener correctamente la multimedia y devolver
# true or false.
# En un futuro podria usarse para convertir los bytes del archivo en un cadena Base64 y enviarla a otro lado
def get_multimedia_item_test(id):
    # Optional headers
    # Mime-Type: "image/jpeg"   (e.g. Convert tiff to jpeg)
    # Verification: "TimeStamp"
    ####
    endpoint = api_base_url + "/dms/documents/" + str(id) + "/item"
    response = None
    try:
        response = session.get(
            endpoint, headers=base_headers, verify=verify_ssl, stream=False)
        if (response.status_code == 200):
            item_data = BytesIO()
            for chunk in response.iter_content(chunk_size=65536):
                item_data.write(chunk)

            item_data.seek(0)
            logger.info(
                f"Retrieved multimedia for item {id} - Size: {item_data.getbuffer().nbytes}")

            # Por ahora solo devolvemos que se pudo obtener
            return True
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error getting multimedia item for for document {id}: {error.args}"
        logger.error(msg)
        return False
    finally:
        # Important: Do not forget to close "response" when it's created with "stream=True" flag.
        response.close()


def create_update_item(id, mime_type, binary_data):
    # Important: This endpoint only works in repositories v6.
    # If the document already has a view, it will be replaced
    # data => bytes corresponding to multimedia item.
    # HEADERS
    #   Mime-Type: "image/jpeg"
    #   Mime-Type-Recode: "application/pdf"         - Optional
    #   Content-Type: "application/octet-stream"
    endpoint = api_base_url + "/dms/documents/" + str(id) + "/item"
    custom_headers = base_headers.copy()
    custom_headers["Mime-Type"] = mime_type
    custom_headers["Content-Type"] = "application/octet-stream"
    files = {"file": ("file", binary_data)}
    try:
        response = session.put(
            endpoint, headers=custom_headers, files=files, verify=verify_ssl)
        if (response.status_code == 200):
            # No esta devolviendo un json como dice en la documentacion
            # result = response.json()
            logger.info(f"Item created for document {id}")
            return True
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error creating item for document {id}: {error.args}"
        logger.error(msg)
        return None


def get_workflow_queues(process):
    # In repository v6 there is no workflow to get queues
    endpoint = api_base_url + "/dms/workflow/queues"
    custom_headers = base_headers.copy()
    custom_headers["processname"] = process
    try:
        response = session.get(
            endpoint, headers=custom_headers, verify=verify_ssl)
        if (response.status_code == 200):
            result = response.json()
            nro_queues = result["meta"]["total"]
            logger.info(f"Retrieved workflow queues from DMS ({nro_queues})")
            return result
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error getting workflow queues: {error.args}"
        logger.error(msg)
        return None


#######################################
########### DOCUMENT TYPES ############
#######################################

def get_document_types():
    endpoint = api_base_url + "/dms/types"
    try:
        response = session.get(
            endpoint, headers=base_headers, verify=verify_ssl)
        if (response.status_code == 200):
            logger.info("Retrieved Document Types from DMS")
            return response.json()
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error getting document types from DMS: {error.args}"
        logger.error(msg)
        return None


def get_document_definition(document_name):
    endpoint = api_base_url + "/dms/types/" + document_name
    try:
        response = session.get(
            endpoint, headers=base_headers, verify=verify_ssl)
        if (response.status_code == 200):
            logger.info(f"Retrieved definition for document {document_name}")
            return response.json()
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error getting definition for document {document_name}: {error.args}"
        logger.error(msg)
        return None


#######################################
########## USERS' FUNCTIONS ###########
#######################################

def get_user(user):
    endpoint = api_base_url + "/dms/users/" + user
    try:
        response = session.get(
            endpoint, headers=base_headers, verify=verify_ssl)
        if (response.status_code == 200):
            logger.info(f"Retrieved user {user}")
            return response.json()
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error getting information for user {user}: {error.args}"
        logger.error(msg)
        return None


def get_users():
    # Important: This endpoint only works in repositories v6.
    endpoint = api_base_url + "/dms/users"
    custom_headers = base_headers.copy()
    try:
        custom_headers["onlyMeta"] = "false"
        custom_headers["page"] = "1"
        custom_headers["pageSize"] = "500"
        response = session.get(
            endpoint, headers=custom_headers, verify=verify_ssl)
        if (response.status_code == 200):
            logger.info("Retrieved user's list")
            return response.json()
        else:
            raise Exception(compose_exception(response, endpoint))
    except Exception as error:
        msg = f"Error getting user's list: {error.args}"
        logger.error(msg)
        return None


def update_user_password(data):
    # PUT
    endpoint = api_base_url + "/dms/users"
    pass


def update_user(user, data):
    # PUT
    endpoint = api_base_url + "/dms/users/" + user
    pass


def create_user(data):
    # POST
    endpoint = api_base_url + "/dms/users"
    pass


def delete_user(user):
    # DELETE
    endpoint = api_base_url + "/dms/users/" + user
    pass

## Auxiliar functions ##


def is_valid_dms_error_message(response):
    try:
        _ = response.json()
        return True
    except:
        return False


def compose_exception(response, endpoint):
    if is_valid_dms_error_message(response):
        return response.json()
    else:
        return str(response.status_code) + " - " + response.reason + " - " + endpoint
