# usuario_api.py - API Flask com consultas e observações
import oracledb
from datetime import datetime, date
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite acesso do front-end local


# ==============================
# Conexão com Oracle
# ==============================
def getConnection():
    try:
        return oracledb.connect(
            user="rm559072",
            password="130106",
            host="oracle.fiap.com.br",
            port=1521,
            service_name="orcl"
        )
    except Exception as e:
        print(f'Erro ao conectar: {e}')
        return None


# ==============================
# Consultas
# ==============================
def listar_proximas_consultas_db(cpf):
    conn = getConnection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_consulta,
                   TO_CHAR(data_consulta,'YYYY-MM-DD HH24:MI:SS'),
                   nome_medico,
                   presenca,
                   data_consulta
            FROM consultas
            WHERE cpf_paciente = :cpf
            ORDER BY 
                CASE 
                    WHEN data_consulta >= SYSDATE THEN 0  -- Consultas futuras primeiro
                    ELSE 1                                -- Depois as passadas
                END,
                data_consulta ASC
        """, {'cpf': cpf})
        return cursor.fetchall()
    finally:
        conn.close()


def confirmar_presenca_db(cpf, id_consulta):
    conn = getConnection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE consultas
            SET presenca = 'Confirmada'
            WHERE id_consulta = :id AND cpf_paciente = :cpf
        """, {'id': id_consulta, 'cpf': cpf})
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def cancelar_presenca_db(cpf, id_consulta):
    conn = getConnection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE consultas
            SET presenca = 'Cancelada'
            WHERE id_consulta = :id AND cpf_paciente = :cpf
        """, {'id': id_consulta, 'cpf': cpf})
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# ==============================
# Observações
# ==============================
def listar_observacoes_db(cpf):
    conn = getConnection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_observacao,
                   id_consulta,
                   descricao,
                   TO_CHAR(data_criacao,'YYYY-MM-DD HH24:MI:SS')
            FROM observacoes
            WHERE cpf_paciente = :cpf
            ORDER BY data_criacao DESC
        """, {'cpf': cpf})
        return cursor.fetchall()
    finally:
        conn.close()


def inserir_observacao_db(cpf, id_consulta, descricao):
    conn = getConnection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO observacoes (cpf_paciente, id_consulta, descricao, data_criacao)
            VALUES (:cpf, :id_consulta, :descricao, SYSDATE)
        """, {'cpf': cpf, 'id_consulta': id_consulta, 'descricao': descricao})
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def atualizar_observacao_db(cpf, id_obs, descricao):
    conn = getConnection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE observacoes
            SET descricao = :descricao
            WHERE id_observacao = :id_obs AND cpf_paciente = :cpf
        """, {'descricao': descricao, 'id_obs': id_obs, 'cpf': cpf})
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def excluir_observacao_db(cpf, id_obs):
    conn = getConnection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM observacoes
            WHERE id_observacao = :id_obs AND cpf_paciente = :cpf
        """, {'id_obs': id_obs, 'cpf': cpf})
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# ==============================
# Endpoints Flask
# ==============================
@app.route("/consultas/<cpf>", methods=["GET"])
def api_listar_consultas(cpf):
    consultas = listar_proximas_consultas_db(cpf)
    result = []
    agora = datetime.now()

    for c in consultas:
        id_consulta = c[0]
        data_str = c[1]
        nome_medico = c[2]
        presenca = c[3]
        data_real = c[4]

        # Define status automático
        if data_real.date() == date.today():
            status_automatico = "Hoje"
        elif data_real < agora:
            status_automatico = "Encerrada"
        else:
            status_automatico = "Futura"

        result.append({
            "id": id_consulta,
            "data": data_str,
            "medico": nome_medico,
            "status": presenca if presenca else status_automatico
        })

    return jsonify(result)


@app.route("/consultas/confirmar", methods=["POST"])
def api_confirmar_presenca():
    data = request.json
    success = confirmar_presenca_db(data["cpf"], data["id_consulta"])
    return jsonify({"success": success})


@app.route("/consultas/cancelar", methods=["POST"])
def api_cancelar_presenca():
    data = request.json
    success = cancelar_presenca_db(data["cpf"], data["id_consulta"])
    return jsonify({"success": success})


# ---------- OBSERVAÇÕES ----------
@app.route("/observacoes/<cpf>", methods=["GET"])
def api_listar_observacoes(cpf):
    obs = listar_observacoes_db(cpf)
    result = [{"id_obs": o[0], "id_consulta": o[1], "descricao": o[2], "data": o[3]} for o in obs]
    return jsonify(result)


@app.route("/observacoes", methods=["POST"])
def api_inserir_observacao():
    data = request.json
    success = inserir_observacao_db(data["cpf"], data["id_consulta"], data["descricao"])
    return jsonify({"success": success})


@app.route("/observacoes/atualizar", methods=["POST"])
def api_atualizar_observacao():
    data = request.json
    success = atualizar_observacao_db(data["cpf"], data["id_obs"], data["descricao"])
    return jsonify({"success": success})


@app.route("/observacoes/excluir", methods=["POST"])
def api_excluir_observacao():
    data = request.json
    success = excluir_observacao_db(data["cpf"], data["id_obs"])
    return jsonify({"success": success})

@app.route("/", methods=["GET"])
def home():
    return "API está online!"

# ==============================
# Rodar Flask
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
