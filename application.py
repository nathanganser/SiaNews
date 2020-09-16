from flask import Flask, render_template, request, redirect, send_from_directory
import siaskynet as skynet
import os
from flask_sqlalchemy import SQLAlchemy
import datetime
import webbrowser


application = Flask(__name__)
# application.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE']
application.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db = SQLAlchemy(application)
client = skynet.SkynetClient()


class Upload(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    skylink = db.Column(db.String)
    timestamp = db.Column(db.DateTime)

    def insert(self):
        db.session.add(self)
        db.session.commit()


# URLs
@application.route('/')
def index():
    return render_template('index.html')


@application.route('/upload')
def upload():
    return render_template('upload.html')


@application.route('/skydirect/<string:skylink>')
def skydirect(skylink):
    return webbrowser.open_new_tab("https://siasky.net/" + skylink)


@application.route('/upload-file', methods=['POST'])
def uploader():
    if request.files:
        file = request.files["image"]
        skylink = client.upload_file(file)

        print("Upload successful, skylink: " + skylink)

        uploaded = Upload(skylink, datetime.datetime.now())
        uploaded.insert()

        return redirect('/')


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080, debug=True)
