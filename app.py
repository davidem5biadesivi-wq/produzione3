from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lavorazioni.db'
db = SQLAlchemy(app)

class Lavorazione(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    macchina = db.Column(db.String(50))
    descrizione = db.Column(db.String(200))
    data_richiesta = db.Column(db.String(50))
    operatore = db.Column(db.String(50))
    cliente = db.Column(db.String(100))
    ordine = db.Column(db.String(50))
    codice_articolo = db.Column(db.String(50))
    data_consegna = db.Column(db.String(50))
    notifica = db.Column(db.Boolean, default=False)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    ruolo = request.form['ruolo']
    session['ruolo'] = ruolo
    session['utente'] = request.form['utente']
    if ruolo == 'operatore':
        return redirect(url_for('dashboard_operatore'))
    else:
        return redirect(url_for('dashboard_ufficio'))

@app.route('/operatore', methods=['GET', 'POST'])
def dashboard_operatore():
    utente = session.get('utente')
    if request.method == 'POST':
        lavorazione_id = request.form['id']
        lavorazione = Lavorazione.query.get(lavorazione_id)
        lavorazione.cliente = request.form['cliente']
        lavorazione.ordine = request.form['ordine']
        lavorazione.codice_articolo = request.form['codice_articolo']
        lavorazione.data_consegna = request.form['data_consegna']
        lavorazione.notifica = False
        db.session.commit()
    lavorazioni = Lavorazione.query.filter_by(operatore=utente).all()
    return render_template('pagina_operatore.html', lavorazioni=lavorazioni, utente=utente)

@app.route('/ufficio', methods=['GET', 'POST'])
def dashboard_ufficio():
    filtro = request.args.get('macchina')
    if request.method == 'POST':
        lavorazione_id = request.form['id']
        lavorazione = Lavorazione.query.get(lavorazione_id)
        lavorazione.data_richiesta = request.form['data_richiesta']
        lavorazione.notifica = True
        db.session.commit()
    if filtro:
        lavorazioni = Lavorazione.query.filter_by(macchina=filtro).all()
    else:
        lavorazioni = Lavorazione.query.all()
    return render_template('ufficio.html', lavorazioni=lavorazioni)

@app.route('/inserisci', methods=['POST'])
def inserisci():
    nuova = Lavorazione(
        macchina=request.form['macchina'],
        descrizione=request.form['descrizione'],
        operatore=session.get('utente')
    )
    db.session.add(nuova)
    db.session.commit()
    return redirect(url_for('dashboard_operatore'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
