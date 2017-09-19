"""Mailer script."""
import hashlib
import sys
import os
import smtplib
import urllib2
from optparse import OptionParser
from flask import Flask, request, redirect, url_for, render_template, session
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import encoders
reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
app.secret_key = hashlib.sha1(os.urandom(128)).hexdigest()


@app.route("/", methods=['GET', 'POST'])
def index():
    """Function that handles the Email form."""
    if request.method == 'POST':
        email = request.form['email']
        file_url = request.form['file_url']
        file_name = request.form['file_name']
        mailer(email, file_url, file_name)
        session["data"] = email
        return redirect(url_for('submit'))
    return render_template('index.html')


@app.route("/submit", methods=['GET'])
def submit():
    """Function that redirects to success page."""
    return render_template('submit.html', data=session["data"])


def mailer(email, file_url, file_name):
    """Function that downloads and emails the file."""
    fromaddr = "your_email"
    toaddr = email
    password = "your_password"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    part = MIMEBase('application', 'octet-stream')
    req = urllib2.Request(
        file_url,
        headers={
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
        })
    part.set_payload(urllib2.urlopen(req).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
                    "attachment; filename= %s" % file_name)
    msg.attach(part)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, password)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option(
        "-p",
        "--port",
        dest="port",
        help="Port on which the app will run",
        default=5000)
    (options, args) = parser.parse_args()
    app.run(host='0.0.0.0', debug=True, port=int(options.port))
