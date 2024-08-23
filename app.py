from flask import Flask, render_template, redirect, request, url_for, session, flash
import os
from flask_cors import CORS
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

from authlib.integrations.flask_client import OAuth
from werkzeug.utils import secure_filename
import random

from deepgrammodule import transcripted_file
from googletrans import Translator
from pydub import AudioSegment



load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

CORS(app)

app.config['DEBUG'] = os.environ.get('FLASK_DEBUG')

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



db = SQLAlchemy(app)
translator = Translator()



app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')
os.makedirs(os.environ.get('UPLOAD_FOLDER'), exist_ok=True)

ALLOWED_EXTENSIONS = {'mp3', 'wav'}



oauth = OAuth(app)
CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration' #provide us with common metadata configurations 
google = oauth.register(
  name='google',
  server_metadata_url=CONF_URL,
  # Collect client_id and client secret from google auth api
  client_id= os.environ.get("GOOGLE_CLIENT_ID"),
  client_secret = os.environ.get("GOOGLE_CLIENT_SECRET"),
  client_kwargs={
    'scope': 'openid email profile'
  }
)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=True)
    score = db.Column(db.Float, nullable=False, default=0.0)
    audio_files = db.relationship('FileDetails', backref='user', lazy=True)
    transcripts = db.relationship('Transcript', backref='user', lazy=True)


class FileDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transcript = db.relationship('Transcript', backref='file_details', uselist=False)

class Transcript(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transcript = db.Column(db.Text, nullable=False)
    original_transcript = db.Column(db.Text, nullable=False, default="")
    original_language = db.Column(db.String(80), nullable=False, default="en")
    sentences = db.Column(db.Text, nullable=False)
    duration = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('file_details.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'transcript': self.transcript,
            'original_transcript': self.original_transcript,
            'original_language': self.original_language,
            'sentences': self.sentences,
            'duration': self.duration,
            'user_id': self.user_id,
            'filename': self.file_details.filename
        }




@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/check")
def check():
    return render_template("check.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email, password=password).first()
        if user:
    
            session["user_id"] = user.id
            session["email"] = user.email
            session["name"] = user.full_name

            return redirect(url_for("dashboard", user_id=user.id))
        else:
            flash("Invalid email or password!! Kindly Try Again")
            return render_template("login.html")
        
    return render_template("login.html")

@app.route('/google/login')
def google_login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/callback')
def authorize():
    token = google.authorize_access_token()  # Get the access token
    user_info = token['userinfo']  # Fetch user information

    # Store user information in session
    session['email'] = user_info['email']
    session['name'] = user_info['name']


    email = user_info['email']
    name = user_info['name']
    
    user = User.query.filter_by(email=email).first()
    if user:
        session['user_id'] = user.id
        return redirect(url_for('dashboard', user_id=user.id))
    else:
        new_user = User(full_name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id

        return redirect(url_for('dashboard', user_id=new_user.id))



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        old_user = User.query.filter_by(email=email).first()

        if old_user:
            flash("User with this email already exists. Please login or Use different email ")
            return redirect(url_for("login"))

        new_user = User(full_name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop('email', None)
    session.pop('name', None)
    session.pop('user_id', None)
    return render_template("login.html")


def get_top3_phrases(transcripts):
    return ['Phrase1', 'Phrase2', 'Phrase3']

def get_similar_users(transcripts):
    return ['User1', 'User2', 'User3']


@app.route("/dashboard/<int:user_id>")
def dashboard(user_id):
    name=session.get("name")

    user_transcripts = Transcript.query.filter_by(user_id=user_id).all()
    user_transcripts = [transcript.to_dict() for transcript in user_transcripts]
    sentences = [t['sentences'] for t in user_transcripts]

    frequency_table = get_frequency_table(user_transcripts)
    user_score = sum(frequency_table.values()) / len(frequency_table) if frequency_table else 0
    user = User.query.filter_by(id=user_id).first()
    user.score = user_score
    db.session.commit()


    top3_phrases = get_top3_phrases(sentences, frequency_table)
    

    similar_users = get_similar_users(user_score, user_id)

    return render_template("dashboard.html", user_id=user_id, name=name, top3_phrases=top3_phrases, similar_users=similar_users, user_transcripts=user_transcripts, frequency_table=frequency_table)

def get_frequency_table(user_transcripts):
    all_transcripts = Transcript.query.all()
    all_transcripts = [transcript.to_dict()['transcript'] for transcript in all_transcripts]
    user_transcripts = [t['transcript'] for t in user_transcripts]


    user_words = {}
    for transcript in user_transcripts:
        for word in transcript.split():
            if word in user_words:
                user_words[word] += 1
            else:
                user_words[word] = 1

    all_words = {}
    for transcript in all_transcripts:
        for word in transcript.split():
            if word in all_words:
                all_words[word] += 1
            else:
                all_words[word] = 1

    frequency_table = {}
    for word in user_words:
        frequency_table[word] = user_words[word] / all_words[word]

    frequency_table = dict(sorted(frequency_table.items(), key=lambda item: item[1]))



    return frequency_table

def get_top3_phrases(sentences, frequency_table):
    print('getting top 3 phrases invoked')
    if not frequency_table or not sentences:
        print('no frequency table or no sentences')
        return

    sentences = [sentence.split('-') for sentence in sentences]
    # print(sentences, frequency_table)

    top_3_sentences = []

    for word in frequency_table:
        for sentence in sentences:
            if word in sentence[0].split(' ') and sentence not in top_3_sentences:
                top_3_sentences.append(sentence)
                if len(top_3_sentences) == 5:
                    break


    print(top_3_sentences)
    return top_3_sentences

def get_similar_users(user_score, user_id):

    all_other_users = User.query.filter(User.id != user_id).all()

    similar_users = []

    for other_user in all_other_users:
        other_user_score = other_user.score
        if abs(other_user_score-user_score) < 0.125:
            similar_users.append((other_user.full_name, other_user.email))

    return similar_users
            

    





##### Handling Files ######

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    user_id = session.get("user_id")
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # if file and allowed_file(file.filename):
        if file:

            

            filename = secure_filename(file.filename)
            if FileDetails.query.filter_by(filename=filename).first():
                filename = filename.split(".")[0] + str(random.randint(1, 10000)) + "." + filename.split(".")[1]
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Convert WebM to WAV using pydub
            try:
                audio = AudioSegment.from_file(filepath, format="webm")
                wav_filename = filename.rsplit('.', 1)[0] + '.wav'


                if FileDetails.query.filter_by(filename=wav_filename).first():
                    wav_filename = wav_filename.split(".")[0] + str(random.randint(1, 10000)) + "." + wav_filename.split(".")[1]

                wav_filepath = os.path.join(app.config['UPLOAD_FOLDER'], wav_filename)

                if os.path.exists(filepath):
                    os.remove(filepath)
                
                audio.export(wav_filepath, format="wav")

            except Exception as e:
                print(e)
                wav_filename = filename




            new_file = FileDetails(filename=wav_filename, user_id=user_id)
            db.session.add(new_file)
            db.session.commit()

            handle_file(wav_filename, user_id, new_file.id)

            return redirect(url_for('dashboard', user_id=session.get("user_id")))
        else:
            flash('File type not allowed kindly upload .wav, .mp3 file type only')
            return redirect(request.url)
        
    if request.method == 'GET':
        return render_template('upload_audio.html', user_id=session.get("user_id"))
    
def handle_file(filename, user_id, file_id):
    json_file = transcripted_file(filename)
    try:
        original_transcript = json_file['results']['channels'][0]['alternatives'][0]['transcript']
        transcript = original_transcript
        duration = round(json_file['metadata']['duration'],2)
        original_language = json_file["results"]["channels"][0]["detected_language"]
        sentences = json_file["results"]["channels"][0]["alternatives"][0]["paragraphs"]["paragraphs"][0]["sentences"]

        sentences = [sentence["text"] for sentence in sentences]
    

        if original_language != "en":
            transcript = translate(original_transcript)
            sentences = [translate(sentence) for sentence in sentences]

            new_transcript = Transcript(transcript=transcript, original_transcript=original_transcript, original_language=original_language, sentences='-'.join(sentences), duration=duration, user_id=user_id, file_id=file_id)
            db.session.add(new_transcript)
            db.session.commit()

        else:
            new_transcript = Transcript(transcript=transcript,  sentences='-'.join(sentences), duration=duration, user_id=user_id, file_id=file_id)
            db.session.add(new_transcript)
            db.session.commit()

        return redirect(url_for('dashboard', user_id=session.get("user_id")))

    except Exception as e:
        flash('Something is wrong with the audio file not able to transcribe it. Please try again.')
        return redirect(request.url)


def translate(text):
    return translator.translate(text, dest='en').text


@app.route("/micrecording")
def mic_recording():
    if request.method == "POST":
        return redirect(url_for('dashboard', user_id=session.get("user_id")))
    return render_template("micrecording.html", user_id=session.get("user_id"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()