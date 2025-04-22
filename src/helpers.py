import logging
import re
from datetime import datetime, timedelta

# Logging system
logger = logging.getLogger(__name__)


def calculate_and_replace_placeholders(match):
    
    #Replace {SYSTEM_DATE} with actual date or {SYSTEM_DATE,n} with calculated date
    today = datetime.today().strftime("%Y%m%d")

    if match.group(1):  # If there a number in {SYSTEM_DATE,n}
        try:
            # Convertir n a entero (puede ser negativo)
            number_of_days = int(match.group(1))
            calculated_date = (datetime.today() +
                                timedelta(days=number_of_days)).strftime("%Y%m%d")
            return calculated_date
        except ValueError as error:
            logger.error(error)
            return today
    else:
        return today  # Is {SYSTEM_DATE}


"""
It receive a query (string) that may contain interpolated keys which must be calculated and replaced 
with their corresponding values.
Example (system date = 2025-04-15 ):

  Parameter received:
    "( (Expediente_Vehiculos | Expediente_Emision ) & ($operation_date='{SYSTEM_DATE}' | $operation_date={SYSTEM_DATE,1} | $operation_date={SYSTEM_DATE,-5}) )"

  Response:
    "( (Expediente_Vehiculos | Expediente_Emision ) & ($operation_date='20250415' | $operation_date=20250416 | $operation_date=20250410) )"

"""
def parse_dms_query(query):
    response = query
    try:
        #Create pattern to extract keys
        pattern = r"\{\s*system_date\s*(?:,\s*(-?[1-9][0-9]{0,2})\s*)?\}"

        response = re.sub(pattern, calculate_and_replace_placeholders,query, flags=re.IGNORECASE)
    except Exception as error:
        logger.error(error)    
    finally:
        return response
            