import os
import shutil
import zipfile
from coralogger import get_default_logger

log = get_default_logger()


def check_clean_path(local_path, tag):
    if not os.path.exists(local_path):
        os.makedirs(local_path)
        log.debug("%s doesn't exist, creating" % str(local_path))
    full_path = local_path + "/" + tag

    if not os.path.exists(full_path):
        os.makedirs(full_path)
        log.debug("%s doesn't exist, creating" % str(full_path))
    else:
        shutil.rmtree(full_path)
        log.debug("cleaning %s" % str(full_path))
        os.makedirs(full_path)
        log.debug("%s doesn't exist, creating" % str(full_path))


def unzip_file(local_path, full_file_path, tag):
    full_path = local_path + "/" + tag
    zip_ref = zipfile.ZipFile(full_file_path, 'r')
    zip_ref.extractall(full_path)
    if os.path.exists(full_path+"/Dockerfile.nlu"):
        log.debug("%s dockerfile exist" % str(tag))
    else:
        log.debug("%s fail during unziping" % str(tag))
    zip_ref.close()
    os.remove(full_file_path)


def get_training_data_size(full_path, files_list):
    size = 0
    for i in files_list:
        path = full_path + "/" + i
        size += os.path.getsize(path)
    return size
