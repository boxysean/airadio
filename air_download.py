import getpass, os, imaplib, email
import yaml
import sys
import email.utils
from datetime import datetime
import time

from optparse import OptionParser

audio_ext = ["aif", "aiff", "m4a", "mp3", "mpa", "wav", "wma", "flac", "ogg"]

def parseDate(date):
  timetuple = email.utils.parsedate_tz(date)
  return "%04d%02d%02d%02d%02d%02d" % timetuple[0:6]

def isAudioFile(filename):
  split_filename = filename.split(".")
  return len(split_filename) > 0 and split_filename[-1].lower() in audio_ext

def getMsgs(usernm, passwd=None, servername="imap.gmail.com", first=True):
  if not passwd:
    passwd = getpass.getpass()

  conn = imaplib.IMAP4_SSL(servername, 993)
  conn.login(usernm,passwd)
  conn.select()

  if first:
    typ, data = conn.search(None,'ALL')
  else:
    typ, data = conn.search(None,'UnSeen')

  if data[0]:
    print "new message(s)!"

  for num in data[0].split():
    hdata = conn.fetch(num, '(BODY[HEADER.FIELDS (SUBJECT FROM DATE)])')
    header_data = hdata[1][0][1]
    header_data_array = header_data.split("\n")

    print ":::new message details:::"
    print header_data.strip()
    print ":::::::::::::::::::::::::"

    date = filter(lambda x: x.startswith("Date"), header_data_array)[0]
    datestring = parseDate(date[6:])

    typ, data = conn.fetch(num,'(RFC822)')
    msg = email.message_from_string(data[0][1])
    yield (msg, datestring)

def getAttachment(msg):
  for part in msg.walk():
    # return only the first attachment...
    filename = part.get_filename()
    if part.get_content_type().startswith("audio") or (filename and isAudioFile(filename)):
      return filename, part.get_payload(decode=1)
  return (None, None)

def checkEmail(account, password, server, first_run, dest_folder, client=None):
  for msg, datestring in getMsgs(account, passwd=password, servername=server, first=first_run):
    filename, payload = getAttachment(msg)

    filename = datestring + "_" + filename

    if not payload:
      continue

    filepath = dest_folder + os.sep + filename

    if not os.path.isfile(filepath):
      print "writing %s" % (filename)
      fp = open(filepath, 'wb')
      fp.write(payload)
      fp.close()

    if client:
      client.update()
      filename = filepath.split(os.sep)[-1]
      print "[+] add %s" % (filename)
      client.add(filename)

def ezrun(client):
  config = yaml.load(open("air_download.yml", "r"))
  checkEmail(config["account"], config["password"], config["server"], False, config["destination_folder"], client)


if __name__ == '__main__':
  parser = OptionParser()

  parser.add_option("-c", "--config-file", dest="config_file", help="location of config file")
  parser.add_option("-f", "--first", action="store_true", dest="first_run", help="checks all emails in the account", default=False)

  (options, args) = parser.parse_args()

  config = yaml.load(open(options.config_file, "r"))

  checkEmail(config["account"], config["password"], config["server"], options.first_run, config["destination_folder"])
