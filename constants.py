import os

LOCAL_PATH = '/tmp/nlu'
CLOUD_USER = os.environ.get("AWS_ACCESS_KEY_ID")
CLOUD_PASSWORD = os.environ.get("AWS_SECRET_ACCESS_KEY")
DOCKER_REPO = os.environ.get("DOCKER_REPO")
KUBER_CONFIG = os.environ.get("KUBER_CONFIG")
DOMAIN = os.environ.get("DOMAIN")
KUBER_SERVICE_DOMAIN = os.environ.get("KUBER_SERVICE_DOMAIN")
NLU_SECRET_NAME = os.environ.get("NLU_SECRET_NAME")
NAMESPACE = "nlu"
INCLUSTER = os.environ.get("INCLUSTER")

# Logs
CORALOGIX_ENABLED = os.environ.get("CORALOGIX_ENABLED")
CORALOGIX_PRIVATE_KEY = os.environ.get("CORALOGIX_PRIVATE_KEY")
CORALOGIX_SUB_SYSTEM = os.environ.get("CORALOGIX_SUB_SYSTEM")
CORALOGIX_APP_NAME = os.environ.get("CORALOGIX_APP_NAME")

LOGGER_NAME = "KubBuilder Log"

# Log file name
LOG_FILE_PREFIX = "kubbuilder.log"
LOG_FILE_ROOT = "./logs/"

# Log rotation protocol
LOG_ROTATE_WHEN = "H"
LOG_ROTATE_INTERVAL = 1
LOG_FILE_NUM_BACKUPS = 1

LOGGING_SEVERITY = "DEBUG"

# Log formatting
LOG_DEFAULT_FORMAT = '[{levelname} {asctime} {module}:{funcName}:{lineno}] {message}'
LOG_DEFAULT_DATE_FORMAT = '%y-%m-%d %H:%M:%S'

# memmory allocation

MALLOCATION_COEFICIENT = float(0.00004)
MALLOCATION_CONSTANT = float(77.4)
MALLOCATION_ALLOWANCE = float(1.10)
MALLOCATION_FILES = ["intent_train.csv", "entity.csv"]
