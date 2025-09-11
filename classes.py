from database import gerar_hash_senha

class Cliente:
    def __init__(self,cpf,nome,uf,municipio,rua,cep,nascimento,sexo):
        self.cpf = cpf
        self.nome = str(nome)
        self.uf = str(uf)
        self.municipio = str(municipio)
        self.rua = str(rua)
        self.cep = cep
        self.nascimento = nascimento
        self.sexo = str(sexo)
    
    def salvar(self, conn, cur):
        sql = """INSERT INTO clientes
        (cpf,nome_completo,uf,municipio,rua,cep,data_nascimento,sexo)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (cpf) DO NOTHING"""
        valores = (
            str(self.cpf).zfill(11),
            self.nome.upper(),
            self.uf.upper(),
            self.municipio.upper(),
            self.rua.upper(),
            str(self.cep).zfill(8),
            self.nascimento,
            self.sexo.upper()
        )
        cur.execute(sql, valores)
        conn.commit()
    
class Agencia:
    def __init__(self,agencia,uf,municipio,rua,cep):
        self.uf = str(uf)
        self.municipio = str(municipio)
        self.rua = str(rua)
        self.cep = cep
        self.agencia = agencia
    
    def salvar(self, conn, cur):
        sql = """INSERT INTO agencias (uf,numero_agencia,municipio,rua,cep)
                 VALUES (%s,%s,%s,%s,%s)
                 ON CONFLICT (numero_agencia) DO NOTHING"""
        valores = (
            self.uf.upper(),
            self.agencia,
            self.municipio.upper(),
            self.rua.upper(),
            str(self.cep).zfill(8)
        )
        cur.execute(sql, valores)
        conn.commit()
        
class Conta:
    def __init__(self, agencia, conta, senha_conta=None, cpf=None):
        self.agencia = agencia
        self.conta = conta
        self.cpf = str(cpf).zfill(11) if cpf else None
        self.senha_conta = gerar_hash_senha(senha_conta) if senha_conta else None

    def salvar(self, conn, cur):
        sql = """INSERT INTO contas (cpf,numero_agencia,saldo,hash,numero_conta)
                 VALUES (%s,%s,%s,%s,%s)"""
        cur.execute(sql, (self.cpf, self.agencia, 0, self.senha_conta, self.conta))
        conn.commit()

    def acessar(self, conta, cur):
        cur.execute("""SELECT hash FROM contas
                          WHERE numero_agencia = %s AND numero_conta = %s""",
                       (self.agencia, conta))
        row = cur.fetchone()
        if not row:
            return False
        return self.senha_conta == row[0]
        
    def saque_conta(self, conn, cur, conta, valor, mensagem=None):
        cur.execute("""UPDATE contas
                          SET saldo = saldo - %s
                          WHERE numero_agencia = %s AND numero_conta = %s AND saldo >= %s
                          RETURNING saldo""",
                       (valor, self.agencia, conta, valor))
        row = cur.fetchone()
        if not row:
            return None
        conn.commit()
        return float(row[0])
            
    def deposito(self, conn, cur, conta, valor, mensagem=None):
        cur.execute("""UPDATE contas
                          SET saldo = saldo + %s
                          WHERE numero_agencia = %s AND numero_conta = %s
                          RETURNING saldo""",
                       (valor, self.agencia, conta))
        row = cur.fetchone()
        conn.commit()
        return float(row[0]) if row else None
    
    def saldo(self, cur, conta):
        cur.execute("""SELECT saldo FROM contas
                          WHERE numero_agencia = %s AND numero_conta = %s""",
                       (self.agencia, conta))
        row = cur.fetchone()
        return float(row[0]) if row else None
        
