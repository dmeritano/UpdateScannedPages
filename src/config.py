import logging
class Config():

    # Logging system
    logger = logging.getLogger(__name__)

    # Json parameters - Used internally in this class
    PARAM_DMS_URI = "dmsUri"
    PARAM_DMS_USER = "dmsUser"
    PARAM_DMS_PASS = "dmsPass"
    PARAM_DMS_QUERY = "dmsQuery"
    PARAM_DMS_QUERY_PAGE_SIZE = "queryPageSize"
    PARAM_TEMP_FOLDER = "tempFolder"
    PARAM_SECONDS_BETWEEN_PROCESSED_DOCUMENTS = "secondsBetweenProcessedDocuments"
    PARAM_SEND_EMAIL_NOTIFICATIONS = "sendEmailNotifications"
    

    app_cfg = None

    def __init__(self, cfg):
        self.app_cfg = cfg

    # Json values - Return
    def get_dms_uri(self):
        return self.app_cfg[self.PARAM_DMS_URI]

    def get_dmsuser_name(self):
        return self.app_cfg[self.PARAM_DMS_USER]

    def get_dmsuser_pass(self):
        return self.app_cfg[self.PARAM_DMS_PASS]

    def get_query(self):
        return self.app_cfg[self.PARAM_DMS_QUERY]
     
    def get_query_pagesize(self):
        default = 100
        value = self.app_cfg[self.PARAM_DMS_QUERY_PAGE_SIZE]    
        if isinstance(value, int):
            if value > 0 and value <= 1000:
                return value    
        
        self.logger.warning(f"Invalid value for {self.PARAM_DMS_QUERY_PAGE_SIZE} parameter {value}. Using default {default}")
        return default        
    

    def get_temp_folder(self):
        return self.app_cfg[self.PARAM_TEMP_FOLDER]
    
    def get_delay(self):
        default = 0.2
        value = self.app_cfg[self.PARAM_SECONDS_BETWEEN_PROCESSED_DOCUMENTS]
        if not isinstance(value,int) and not isinstance(value, float):
            return default
        
        value = float(value)
        if value < 0 or value > 2:
            return default
        else:
            return value

    def get_send_email(self):
        return bool(self.app_cfg[self.PARAM_SEND_EMAIL_NOTIFICATIONS])
