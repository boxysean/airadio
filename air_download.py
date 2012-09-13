import getpass, os, imaplib, smtplib, email
import yaml
import sys
import email.utils
from email.parser import HeaderParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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

    print ""
    print ":::new message details:::"
    print header_data.strip()
    print ":::::::::::::::::::::::::"

    date = filter(lambda x: x.startswith("Date"), header_data_array)[0]
    datestring = parseDate(date[6:])

    parser = HeaderParser()
    parsed_header_data = parser.parsestr(header_data)
    origin = parsed_header_data['From']
    sender = email.utils.parseaddr(origin)[1]

    typ, data = conn.fetch(num,'(RFC822)')
    msg = email.message_from_string(data[0][1])
    yield (msg, datestring, sender)

def getAttachment(msg):
  for part in msg.walk():
    # return only the first attachment...
    filename = part.get_filename()
    filename_encoding = part["Content-Transfer-Encoding"]
    if filename_encoding and filename_encoding == "base64":
      if filename and "utf-8" in filename:
        filename = filename[10:-2].decode("base64")
    if part.get_content_type().startswith("audio") or (filename and isAudioFile(filename)):
      return filename, part.get_payload(decode=1)
  return (None, None)

def checkEmail(account, password, server, first_run, dest_folder, respond_to_emails, smtp_server, response_text):
  res = []

  if respond_to_emails and smtp_server:
    conn_res = smtplib.SMTP_SSL(smtp_server, 465)
    conn_res.login(account, password)

  for msg, datestring, sender in getMsgs(account, passwd=password, servername=server, first=first_run):
    filename, payload = getAttachment(msg)

    if not payload:
      continue

    filename = datestring + "_" + filename
    filepath = dest_folder + os.sep + filename

    if not os.path.isfile(filepath):
      print "[<] writing %s" % (filename)
      fp = open(filepath, 'wb')
      fp.write(payload)
      fp.close()
      res.append(filepath.split(os.sep)[-1])

      if respond_to_emails and smtp_server:
        try:
          response = response_text
          data = MIMEMultipart()
          data['Subject'] = 'Thanks from %s' % (account)
          data['From'] = account + '@gmail.com'
          data['To'] = sender

          data.attach(MIMEText(response, 'plain'))

          conn_res.sendmail(account, sender, data.as_string())
          print "::: Sent thank you email"

        except Exception, e:
          print 'Failed to send email response because of:  ', e


  return res

def ezrun(disable_response_to_emails = False):
  config = yaml.load(open("air_download.conf", "r"))

  try:
    respond_to_emails = config["respond_to_emails"]
    smtp_server = config["smtp_server"]
    response_text = config["response_text"]

  except KeyError:
    respond_to_emails = False
    smtp_server = None
    response_text = 'Hvala!'

  if disable_response_to_emails:
    respond_to_emails = False

  return checkEmail(config["account"], config["password"], config["server"], False, config["destination_folder"], respond_to_emails, smtp_server, response_text)


if __name__ == '__main__':
  parser = OptionParser()

  parser.add_option("-c", "--config-file", dest="config_file", help="location of config file")
  parser.add_option("-f", "--first", action="store_true", dest="first_run", help="checks all emails in the account", default=False)

  (options, args) = parser.parse_args()

  config = yaml.load(open(options.config_file, "r"))

  try:
    respond_to_emails = config["respond_to_emails"]
    smtp_server = config["smtp_server"]
    response_text = config["response_text"]

  except KeyError:
    respond_to_emails = False
    smtp_server = None
    response_text = 'Hvala!'


  checkEmail(config["account"], config["password"], config["server"], options.first_run, config["destination_folder"], respond_to_emails, smtp_server, response_text)

