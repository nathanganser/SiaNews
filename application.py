from flask import Flask, render_template, request, redirect
import siaskynet as skynet
import os
from flask_sqlalchemy import SQLAlchemy
import datetime
import webbrowser


application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE']
application.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db = SQLAlchemy(application)
client = skynet.SkynetClient()


class Upload(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    skylink = db.Column(db.String)
    timestamp = db.Column(db.DateTime)
    title = db.Column(db.String)
    clicks = db.Column(db.Integer)
    upvotes = db.Column(db.Integer)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def save(self):
        db.session.commit()



# URLs
@application.route('/')
def index():
    uploads = Upload.query.filter(Upload.timestamp > datetime.date.today()).order_by(Upload.clicks.desc()).all()
    return render_template('index.html', uploads=uploads)


@application.route('/upload')
def upload():
    return render_template('upload.html')


@application.route('/skydirect/<string:skylink>')
def skydirect(skylink):
    upload = Upload.query.filter_by(skylink=skylink).first()
    upload.clicks += 1
    upload.save()

    return redirect("https://siasky.net/" + skylink)


@application.route('/upload-file', methods=['POST'])
def uploader():
    if request.files:
        file = request.files["file"]
        file.save(os.path.join("./files", file.filename))
        title = request.values["title"]
        skylink = client.upload_file("./files/" + file.filename)
        os.remove("./files/" + file.filename)
        clean_link = skylink.replace("sia://", "")

        uploaded = Upload(skylink=clean_link, timestamp=datetime.datetime.now(), title=title, clicks=0, upvotes=0)
        uploaded.insert()

        return redirect('/')


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080, debug=True)