"""Mailer script."""
import hashlib
import os
import smtplib
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = hashlib.sha1(os.urandom(128)).hexdigest()


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    """Function that handles the Email form."""
    if request.method == "POST":
        email: str = request.form["email"]
        file_url: str = request.form["file_url"]
        file_name: str = request.form["file_name"]
        mailer(email, file_url, file_name)
        session["data"] = email
        return redirect(url_for("submit"))
    return render_template("index.html")


@app.route("/submit", methods=["GET"])
def submit() -> str:
    """Function that redirects to the success page."""
    return render_template("submit.html", data=session["data"])


def mailer(email: str, file_url: str, file_name: str) -> None:
    """Function that downloads and emails the file."""
    fromaddr: str = "your_email"
    toaddr: str = email
    password: str = "your_password"
    msg: MIMEMultipart = MIMEMultipart()
    msg["From"] = fromaddr
    msg["To"] = toaddr
    part: MIMEBase = MIMEBase("application", "octet-stream")
    parsed_uri = urlparse(file_url)
    if parsed_uri.hostname == "freetamilebooks.com":
        req: Request = Request(
            file_url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
            },
        )
        part.set_payload(urlopen(req).read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment; filename= %s" % file_name)
        msg.attach(part)
        server: smtplib.SMTP = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(fromaddr, password)
        text: str = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()


if __name__ == "__main__":
    from optparse import OptionParser

    parser: OptionParser = OptionParser()
    parser.add_option(
        "-p", "--port", dest="port", help="Port on which the app will run", default=5000
    )
    (options, args) = parser.parse_args()
    app.run(host="0.0.0.0", debug=True, port=int(options.port))
