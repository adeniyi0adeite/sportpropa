import smtplib

server = smtplib.SMTP('smtp.mailgun.org', 587)
server.starttls()
server.login('postmaster@sportpropa.com', '99fb2e28dc6e657d3ce7a505b47c443f-91fbbdba-90f7b9b4')
server.sendmail('admin@sportpropa.com', 'kingskillash@gmail.com', 'Subject: Test\n\nThis is a test email.')
server.quit()