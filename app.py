from flask import Flask, render_template, request, redirect, url_for, session
from twilio.twiml.voice_response import VoiceResponse, Dial
import csv
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key

SIP_DOMAIN = "microsiptwilio.sip.twilio.com"

contacts = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global contacts
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return "No file uploaded", 400
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        reader = csv.DictReader(stream)
        contacts = []
        for row in reader:
            # Expecting name and phone columns
            name = row.get('name', '').strip()
            phone = row.get('phone', '').strip().replace('+', '')  # Remove + for SIP URI
            if name and phone:
                contacts.append({'name': name, 'phone': phone})
        return redirect(url_for('index'))
    return render_template('index.html', contacts=contacts)

@app.route('/call', methods=['POST'])
def call():
    phone = request.form.get('phone')
    if not phone:
        return "Phone number missing", 400
    session['call_phone'] = phone
    return "Call number saved. Waiting for Twilio webhook.", 200

@app.route('/voice', methods=['POST', 'GET'])
def voice():
    phone = session.get('call_phone')
    resp = VoiceResponse()
    if phone:
        dial = Dial()
        # Dial via SIP URI on your Twilio SIP Domain
        dial.sip(f"sip:{phone}@{SIP_DOMAIN}")
        resp.append(dial)
    else:
        resp.say("No phone number found to call.")
    return str(resp), 200, {'Content-Type': 'application/xml'}

if __name__ == '__main__':
    app.run(debug=True)
