from flask import Flask, request, render_template
from flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'connectjerry2022@gmail.com'
app.config['MAIL_PASSWORD'] = 'ilovechisom360'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


@app.route('/newsletter', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('jerrysite/contacts.html')
    elif request.method == 'POST':
        message = request.form.get('message')
        subject = request.form.get('subject')
        list_of_subscribers = []
        my_email = 'connectjerry2022@gmail.com'

        msg = Message(subject=subject, sender=my_email, recipients=list_of_subscribers)
        msg.body = message
        mail.send(msg)
        return "Sent"


if __name__ == '__main__':
    app.run(debug=True)
