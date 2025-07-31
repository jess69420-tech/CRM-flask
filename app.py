from flask import Flask, render_template, request, redirect, url_for, session
from twilio.twiml.voice_response import VoiceResponse, Dial
import csv
import io
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace this with a real secret key

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
            name = row.get('name', '').strip()
            phone = row.get('phone', '').strip().replace('+', '')
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
    return "Call number saved. Now call your Twilio number.", 200

@app.route('/voice', methods=['POST', 'GET'])
def voice():
    phone = session.get('call_phone')
    resp = VoiceResponse()
    if phone:
        dial = Dial()
        dial.sip(f"sip:{phone}@{SIP_DOMAIN}")
        resp.append(dial)
    else:
        resp.say("No phone number was saved.")
    return str(resp), 200, {'Content-Type': 'application/xml'}

# Required for Render: bind to 0.0.0.0 and pick up assigned port
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
