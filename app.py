from flask import Flask, render_template, request, redirect, url_for
from twilio.twiml.voice_response import VoiceResponse, Dial
import csv
import io
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong random key

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
    # This endpoint no longer needs to store the number in session or anywhere
    # Just respond OK. The real call routing is handled by Twilio webhook.
    return "OK", 200

@app.route('/voice', methods=['GET', 'POST'])
def voice():
    phone = request.args.get('phone')  # Get phone number from query param
    resp = VoiceResponse()
    if phone:
        dial = Dial()
        dial.sip(f"sip:{phone}@{SIP_DOMAIN}")
        resp.append(dial)
    else:
        resp.say("No phone number provided.")
    return str(resp), 200, {'Content-Type': 'application/xml'}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
