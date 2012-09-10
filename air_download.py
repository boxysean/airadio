import getpass, os, imaplib, email
import yaml
import sys

from optparse import OptionParser

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

  if data:
    print "new message(s)!"

  for num in data[0].split():
    hdata = conn.fetch(num, '(BODY[HEADER.FIELDS (SUBJECT FROM DATE)])')
    header_data = hdata[1][0][1]
    print header_data

    typ, data = conn.fetch(num,'(RFC822)')
    msg = email.message_from_string(data[0][1])
    yield msg

def getAttachment(msg):
  for part in msg.walk():
    # return only the first attachment...
    if part.get_content_type().startswith("audio"):
      return part.get_filename(), part.get_payload(decode=1)
  return (None, None)

def checkEmail(account, password, server, first_run, dest_folder, callback=None):
  for msg in getMsgs(account, passwd=password, servername=server, first=first_run):
    filename, payload = getAttachment(msg)

    if not payload:
      continue

    filepath = dest_folder + os.sep + filename

    # Fri, 7 Sep 2012 12:28:21 +0200
    print "from date", msg["date"], type(msg["date"])
    if not os.path.isfile(filepath):
      print "writing %s" % (filename)
      fp = open(filepath, 'wb')
      fp.write(payload)
      fp.close()

    if callback:
      callback(filepath)

def ezrun(callback):
  config = yaml.load(open("air_download.yml", "r"))
  checkEmail(config["account"], config["password"], config["server"], False, config["destination_folder"], callback)


if __name__ == '__main__':
  parser = OptionParser()

  parser.add_option("-c", "--config-file", dest="config_file", help="location of config file")
  parser.add_option("-f", "--first", action="store_true", dest="first_run", help="checks all emails in the account", default=False)

  (options, args) = parser.parse_args()

  config = yaml.load(open(options.config_file, "r"))

  checkEmail(config["account"], config["password"], config["server"], options.first_run, config["destination_folder"])

