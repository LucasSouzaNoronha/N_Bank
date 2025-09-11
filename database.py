import psycopg2
import hashlib
# Mapeamento de DDDs para UFs do Brasil
uf_ddd_map = {
    "AC": 68,
    "AL": 82,
    "AP": 96,
    "AM": 92,
    "BA": 71,
    "CE": 85,
    "DF": 61,
    "ES": 27,
    "GO": 61,
    "MA": 98,
    "MT": 65,
    "MS": 67,
    "MG": 31,
    "PA": 91,
    "PB": 83,
    "PR": 41,
    "PE": 81,
    "PI": 86,
    "RJ": 21,
    "RN": 84,
    "RS": 51,
    "RO": 69,
    "RR": 95,
    "SC": 47,
    "SP": 11,
    "SE": 79,
    "TO": 63
}

class Banco:
    def __init__(self):
        # Parâmetros do docker-compose.yml
        self.dbname = "teste"
        self.user = "teste"
        self.password = "teste"
        self.host = "localhost"
        self.port = 5432

    def criar_banco(self):
        conn = self.conectar()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS agencias (
            id_agencia SERIAL PRIMARY KEY,
            numero_agencia INTEGER NOT NULL UNIQUE,
            uf CHAR(2),
            municipio TEXT,
            rua TEXT,
            cep CHAR(8)
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes(
            cpf CHAR(11) PRIMARY KEY,
            nome_completo TEXT,
            uf CHAR(2),
            municipio TEXT,
            rua TEXT,
            cep CHAR(8),
            data_nascimento DATE,
            sexo CHAR(1) CHECK (sexo IN ('M','F','O'))
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS contas(
            id_conta SERIAL PRIMARY KEY,
            numero_conta INTEGER NOT NULL,
            cpf CHAR(11) REFERENCES clientes(cpf),
            numero_agencia INTEGER REFERENCES agencias(numero_agencia),
            saldo NUMERIC(14,2) DEFAULT 0,
            hash TEXT,
            UNIQUE (numero_agencia, numero_conta)
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS transferencias(
            id_transferencia SERIAL PRIMARY KEY,
            id_conta_saida INTEGER REFERENCES contas(id_conta),
            id_conta_entrada INTEGER REFERENCES contas(id_conta),
            valor NUMERIC(14,2),
            data TIMESTAMP DEFAULT NOW()
        );
        """)
        conn.commit()
        cur.close()
        conn.close()

    def conectar(self):
        return psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
      
    
def gerar_hash_senha(senha_conta):
    return hashlib.sha256(senha_conta.encode('utf-8')).hexdigest()

def pesquisar_uf_agencia(cur, uf):
    cur.execute("SELECT 1 FROM agencias WHERE uf = %s LIMIT 1", (uf,))
    return cur.fetchone() is not None

def gerar_agencia(cur, uf):
    cur.execute("SELECT max(numero_agencia) FROM agencias WHERE uf = %s", (uf,))
    agencia = cur.fetchone()[0]
    if agencia:
        return agencia + 10
    base = str(uf_ddd_map[uf]) + "10"
    return int(base)           
        
def pesquisar_agencia(cur, agencia):
    cur.execute("SELECT 1 FROM agencias WHERE numero_agencia = %s", (agencia,))
    return cur.fetchone() is not None

def gerar_conta(cur, agencia):
    if not pesquisar_agencia(cur, agencia):
        return None
    cur.execute("SELECT max(numero_conta) FROM contas WHERE numero_agencia = %s", (agencia,))
    conta = cur.fetchone()[0]
    return 1000 if conta is None else conta + 1
        
def valida_cpf(num_cpf):
    if len(num_cpf) != 11 or num_cpf.count(num_cpf[0]) == 11:
        return False
    soma = sum(int(num_cpf[i]) * (10 - i) for i in range(9))
    resto = 11 - (soma % 11)
    dig1 = 0 if resto in (10, 11) else resto
    soma = sum(int(num_cpf[i]) * (11 - i) for i in range(10))
    resto = 11 - (soma % 11)
    dig2 = 0 if resto in (10, 11) else resto
    return dig1 == int(num_cpf[9]) and dig2 == int(num_cpf[10])

    