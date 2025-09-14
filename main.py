import json
import database as db
import classes as cl

def correntista(entrada_json):
    try:
        if isinstance(entrada_json, dict):
            dados = entrada_json
        else:
            dados = json.loads(entrada_json)
        campos_obrigatorios = ["cpf", "nome", "uf", "municipio", "endereco", "cep", "nascimento", "sexo"]
        ausentes = [campo for campo in campos_obrigatorios if dados.get(campo) is None]
        if ausentes:
            return json.dumps({"status": "erro", "mensagem": f"Campos obrigatórios ausentes: {', '.join(ausentes)}"})
        cpf = dados.get("cpf")
        cpf_valido = db.valida_cpf(cpf)
        if cpf_valido is True:
            cliente = cl.Cliente(
                int(cpf),
                dados.get("nome"),
                dados.get("uf"),
                dados.get("municipio"),
                dados.get("endereco"),
                int(dados.get("cep")),
                dados.get("nascimento"),
                dados.get("sexo")
            )
            banco = db.Banco()
            try:
                conn = banco.conectar()
                cur = conn.cursor()
            except Exception as erro_banco:
                return json.dumps({"status": "erro", "mensagem": f"Erro ao conectar ao banco de dados: {erro_banco}"})
            try:
                cliente.salvar(conn, cur)
                conn.commit()
                cur.close()
                return json.dumps({"status": "sucesso", "mensagem": "Correntista salvo com sucesso."})
            except Exception as erro_salvar:
                return json.dumps({"status": "erro", "mensagem": f"Erro ao salvar correntista: {erro_salvar}"})
        else:
            return json.dumps({"status": "erro", "mensagem": "CPF inválido. Corrija e tente novamente."})
    except Exception as erro:
        return json.dumps({"status": "erro", "mensagem": str(erro)})

def agencia(entrada_json):
    try:
        if isinstance(entrada_json, dict):
            dados = entrada_json
        else:
            dados = json.loads(entrada_json)
        campos_obrigatorios = ["uf", "municipio", "endereco", "cep"]
        ausentes = [campo for campo in campos_obrigatorios if dados.get(campo) is None]
        if ausentes:
            return json.dumps({"status": "erro", "mensagem": f"Campos obrigatórios ausentes: {', '.join(ausentes)}"})
        uf = dados.get("uf").upper()
        banco = db.Banco()
        try:
            conn = banco.conectar()
            cur = conn.cursor()
        except Exception as erro_banco:
            return json.dumps({"status": "erro", "mensagem": f"Erro ao conectar ao banco de dados: {erro_banco}"})
        numero_agencia = db.gerar_agencia(cur, uf)
        if numero_agencia is None:
            return json.dumps({"status": "erro", "mensagem": "Não foi possível gerar número de agência. Tente novamente."})
        agencia_obj = cl.Agencia(
            numero_agencia,
            uf,
            dados.get("municipio"),
            dados.get("endereco"),
            int(dados.get("cep"))
        )
        agencia_obj.salvar(conn, cur)
        conn.commit()
        conn.close()
        return json.dumps({"status": "sucesso", "mensagem": "Agência salva com sucesso.", "numero_agencia": numero_agencia})
    except Exception as erro:
        return json.dumps({"status": "erro", "mensagem": str(erro)})

def conta(entrada_json):
    try:
        if isinstance(entrada_json, dict):
            dados = entrada_json
        else:
            dados = json.loads(entrada_json)
        campos_obrigatorios = ["agencia", "senha", "cpf"]
        ausentes = [campo for campo in campos_obrigatorios if dados.get(campo) is None]
        if ausentes:
            return json.dumps({"status": "erro", "mensagem": f"Campos obrigatórios ausentes: {', '.join(ausentes)}"})
        agencia = int(dados.get("agencia"))
        banco = db.Banco()
        try:
            conn = banco.conectar()
            cur = conn.cursor()
        except Exception as erro_banco:
            return json.dumps({"status": "erro", "mensagem": f"Erro ao conectar ao banco de dados: {erro_banco}"})
        numero_conta = db.gerar_conta(cur, agencia)
        if numero_conta is None:
            return json.dumps({"status": "erro", "mensagem": "Não foi possível gerar número de conta. Tente novamente."})
        conta_obj = cl.Conta(
            agencia,
            numero_conta,
            dados.get("senha"),
            int(dados.get("cpf"))
        )
        conta_obj.salvar(conn, cur)
        conn.commit()
        conn.close()
        return json.dumps({"status": "sucesso", "mensagem": "Conta salva com sucesso.", "numero_conta": numero_conta})
    except Exception as erro:
        return json.dumps({"status": "erro", "mensagem": str(erro)})

def acessar(entrada_json):
    try:
        if isinstance(entrada_json, dict):
            dados = entrada_json
        else:
            dados = json.loads(entrada_json)
        campos_obrigatorios = ["agencia", "conta", "senha"]
        ausentes = [campo for campo in campos_obrigatorios if dados.get(campo) is None]
        if ausentes:
            return json.dumps({"status": "erro", "mensagem": f"Campos obrigatórios ausentes: {', '.join(ausentes)}"})
        agencia = int(dados.get("agencia"))
        conta = int(dados.get("conta"))
        senha = dados.get("senha")
        banco = db.Banco()
        try:
            conn = banco.conectar()
            cur = conn.cursor()
        except Exception as erro_banco:
            return json.dumps({"status": "erro", "mensagem": f"Erro ao conectar ao banco de dados: {erro_banco}"})
        conta_obj = cl.Conta(agencia, conta, senha)
        acesso = conta_obj.acessar(conta, cur)
        if acesso:
            nome_cliente = db.pesquisar_nome_cliente(cur, agencia, conta)
            return json.dumps({"status": "sucesso", "mensagem": "Acesso autorizado.", "nome_cliente": nome_cliente})
        else:
            return json.dumps({"status": "erro", "mensagem": "Acesso negado."})
    except Exception as erro:
        return json.dumps({"status": "erro", "mensagem": str(erro)})

def transferencia(entrada_json):
    try:
        if isinstance(entrada_json, dict):
            dados = entrada_json
        else:
            dados = json.loads(entrada_json)
        campos_obrigatorios = ["agencia_origem", "conta_origem", "senha", "agencia_destino", "conta_destino", "valor"]
        ausentes = [campo for campo in campos_obrigatorios if dados.get(campo) is None]
        if ausentes:
            return json.dumps({"status": "erro", "mensagem": f"Campos obrigatórios ausentes: {', '.join(ausentes)}"})
        agencia_origem = int(dados.get("agencia_origem"))
        conta_origem = int(dados.get("conta_origem"))
        senha = dados.get("senha")
        agencia_destino = int(dados.get("agencia_destino"))
        conta_destino = int(dados.get("conta_destino"))
        valor = float(dados.get("valor"))
        banco = db.Banco()
        try:
            conn = banco.conectar()
            cur = conn.cursor()
        except Exception as erro_banco:
            return json.dumps({"status": "erro", "mensagem": f"Erro ao conectar ao banco de dados: {erro_banco}"})
        conta_dest = cl.Conta(agencia_destino, conta_destino)
        conta_obj = cl.Conta(agencia_origem, conta_origem, senha)
        acesso = conta_obj.acessar(conta_origem, cur)
        if not acesso:
            return json.dumps({"status": "erro", "mensagem": "Acesso negado."})
        saldo_atual = conta_obj.saque_conta(cur, conta_origem, valor)
        if saldo_atual is None:
            return json.dumps({"status": "erro", "mensagem": "Saldo insuficiente."})
        conta_dest.deposito(cur, conta_destino, valor)
        conn.commit()
        conn.close()
        return json.dumps({"status": "sucesso", "mensagem": "Transferência realizada com sucesso.", "saldo_atual": saldo_atual})
    except Exception as erro:
        return json.dumps({"status": "erro", "mensagem": str(erro)})

def depositar(entrada_json):
    try:
        if isinstance(entrada_json, dict):
            dados = entrada_json
        else:
            dados = json.loads(entrada_json)

        campos_obrigatorios = ["agencia", "conta", "valor", "senha"]
        ausentes = [campo for campo in campos_obrigatorios if dados.get(campo) is None]
        if ausentes:
            return json.dumps({"status": "erro", "mensagem": f"Campos obrigatórios ausentes: {', '.join(ausentes)}"})
        
        agencia = int(dados.get("agencia"))
        conta = int(dados.get("conta"))
        valor = float(dados.get("valor"))
        senha = dados.get("senha")

        banco = db.Banco()
        try:
            conn = banco.conectar()
            cur = conn.cursor()
        except Exception as erro_banco:
            return json.dumps({"status": "erro", "mensagem": f"Erro ao conectar ao banco de dados: {erro_banco}"})
        
        conta_obj = cl.Conta(agencia, conta, senha)
        
        acesso = conta_obj.acessar(conta, cur)
        
        if not acesso:
            return json.dumps({"status": "erro", "mensagem": "Acesso negado. Senha incorreta."})

        conta_obj.deposito(cur, conta, valor)
        conn.commit()
        conn.close()
        return json.dumps({"status": "sucesso", "mensagem": "Deposito realizado com sucesso."})
    except Exception as erro:
        return json.dumps({"status": "erro", "mensagem": str(erro)})
    
def saldo(entrada_json):
    try:
        if isinstance(entrada_json, dict):
            dados = entrada_json
        else:
            dados = json.loads(entrada_json)
        campos_obrigatorios = ["agencia", "conta", "senha"]
        ausentes = [campo for campo in campos_obrigatorios if dados.get(campo) is None]
        if ausentes:
            return json.dumps({"status": "erro", "mensagem": f"Campos obrigatórios ausentes: {', '.join(ausentes)}"})
        agencia = int(dados.get("agencia"))
        conta = int(dados.get("conta"))
        senha = dados.get("senha")
        banco = db.Banco()
        try:
            conn = banco.conectar()
            cur = conn.cursor()
        except Exception as erro_banco:
            return json.dumps({"status": "erro", "mensagem": f"Erro ao conectar ao banco de dados: {erro_banco}"})
        conta_obj = cl.Conta(agencia, conta, senha)
        acesso = conta_obj.acessar(conta, cur)
        if not acesso:
            return json.dumps({"status": "erro", "mensagem": "Acesso negado."})
        saldo_atual = conta_obj.saldo(cur, conta)
        return json.dumps({"status": "sucesso", "saldo": saldo_atual})
    except Exception as erro:
        return json.dumps({"status": "erro", "mensagem": str(erro)})