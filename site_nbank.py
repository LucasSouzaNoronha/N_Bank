from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import main
import json
from database import Banco
from services.requisicoes import buscar_cep

banco = Banco()
banco.criar_banco()

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/dashboard')
def dashboard():
    if 'agencia' not in session:
        return redirect(url_for('acessar'))
    return render_template('dashboard.html')

@app.route('/correntista', methods=['GET', 'POST'])
def correntista():
    if request.method == 'GET':
        return render_template('correntista.html')
    elif request.method == 'POST':
        json_input = request.get_json() or {}
        resultado = main.correntista(json_input)
        return resultado

@app.route('/agencia', methods=['GET', 'POST'])
def agencia():
    if request.method == 'GET':
        return render_template('agencia.html')
    elif request.method == 'POST':
        json_input = request.get_json() or {}
        resultado = main.agencia(json_input)
        return resultado

@app.route('/conta', methods=['GET', 'POST'])
def conta():
    if request.method == 'GET':
        try:
            conn = banco.conectar()
            cur = conn.cursor()
            cur.execute("SELECT numero_agencia, municipio FROM agencias")
            agencias = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            agencias = []
            print(f"Erro ao buscar agências: {e}")

        return render_template('conta.html', agencias=agencias)

    elif request.method == 'POST':
        json_input = request.get_json() or {}
        resultado = main.conta(json_input)
        return resultado
    
@app.route('/acessar', methods=['GET', 'POST'])
def acessar():
    if request.method == 'GET':
        return render_template('acessar.html')
    elif request.method == 'POST':
        json_input = request.get_json() or {}
        resultado = main.acessar(json_input)
        
        resultado_dict = json.loads(resultado)
        if resultado_dict.get('status') == 'sucesso':
            session['agencia'] = json_input.get('agencia')
            session['conta'] = json_input.get('conta')
            session['senha'] = json_input.get('senha')
        
        return resultado

@app.route('/logout')
def logout():
    session.pop('agencia', None)
    session.pop('conta', None)
    session.pop('senha', None)
    return redirect(url_for('home'))

@app.route('/transferencia', methods=['GET', 'POST'])
def transferencia():
    if request.method == 'GET':
        if 'agencia' not in session or 'conta' not in session:
            return redirect(url_for('acessar'))
        return render_template('transferencia.html')
    elif request.method == 'POST':
        if 'agencia' not in session or 'conta' not in session:
            return json.dumps({"status": "erro", "mensagem": "É necessário estar logado para fazer transferências."})
            
        json_input = request.get_json() or {}
        json_input['agencia_origem'] = session.get('agencia')
        json_input['conta_origem'] = session.get('conta')

        resultado = main.transferencia(json_input)
        return resultado

@app.route('/depositar', methods=['GET', 'POST'])
def depositar():
    if request.method == 'GET':
        if 'agencia' not in session or 'conta' not in session:
            return redirect(url_for('acessar'))
        return render_template('depositar.html')
    elif request.method == 'POST':
        if 'agencia' not in session or 'conta' not in session:
            return json.dumps({"status": "erro", "mensagem": "É necessário estar logado para fazer depósitos."})
            
        json_input = request.get_json() or {}
        json_input['agencia'] = session.get('agencia')
        json_input['conta'] = session.get('conta')

        resultado = main.depositar(json_input)
        return resultado

@app.route('/saldo', methods=['POST'])
def saldo():
    json_input = {"agencia": session.get('agencia'),
                  "conta": session.get('conta'),
                  "senha": session.get('senha')}

    resultado = main.saldo(json_input)
    return resultado

@app.route('/buscar_cep', methods=['POST'])
def buscar_cep_route():
    data = request.get_json()
    cep = data.get('cep')
    
    resultado = buscar_cep(cep)
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)
    