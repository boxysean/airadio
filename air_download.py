# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import getpass, os, imaplib, smtplib, email
import yaml
import sys
import email.utils
from email.parser import HeaderParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import time
import email.header

from air_utils import log_it

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
    log_it("new message(s)!")

  for num in data[0].split():
    hdata = conn.fetch(num, '(BODY[HEADER.FIELDS (SUBJECT FROM DATE)])')
    header_data = hdata[1][0][1]
    header_data_array = header_data.split("\n")

    log_it("")
    log_it(":::new message details:::")
    log_it(header_data.strip())
    log_it(":::::::::::::::::::::::::")

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
    filename, filename_encoding = email.header.decode_header(part.get_filename())[0]
    if filename_encoding:
      filename = unicode(filename, filename_encoding)
      filename = filename.encode("ascii", "ignore") # to be nice to file systems
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
      log_it("[<] writing %s" % (filename))
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
          log_it("::: Sent thank you email")

        except Exception, e:
          log_it('Failed to send email response because of:  '+ e)


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

