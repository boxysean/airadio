import getpass, os, imaplib, email

def getMsgs(servername="imap.gmail.com"):
  usernm = "interactivosradio"
  passwd = getpass.getpass()
  conn = imaplib.IMAP4_SSL(servername, 993)
  conn.login(usernm,passwd)
  conn.select()
  typ, data = conn.search(None,'ALL')
  for num in data[0].split():
    typ, data = conn.fetch(num,'(RFC822)')
    msg = email.message_from_string(data[0][1])
    print msg["subject"]
    yield msg

def getAttachment(msg):
  for part in msg.walk():
    print part.get_content_type()
    if part.get_content_type().startswith("audio"):
      return part.get_filename(), part.get_payload(decode=1)

if __name__ == '__main__':
  for msg in getMsgs():
    filename, payload = getAttachment(msg)

    if not payload:
      print "SHOULDN'T BE HERE"
      continue

    print "writing %s" % (filename)
    fp = open(filename, 'wb')
    fp.write(payload)
    fp.close()

