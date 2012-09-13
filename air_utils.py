import logging
import yaml

logger = logging.getLogger('airadio')
hdlr = logging.FileHandler('/var/log/airadio')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

CONFIG = yaml.load(open("air_download.conf", "r"))
try:
  log_to_file = CONFIG["log_to_file"]
except:
  log_to_file = False

def log_it(msg):
  if log_to_file:
    logger.info(msg)
  else:
    print msg
