# ==============================================================
# 🏥 Assistente Virtual HC - API Flask
# ==============================================================

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import oracledb
from datetime import datetime

# ==============================================================
# 1️⃣ Inicialização do App
# ==============================================================
app = Flask(__name__)
CORS(app)


# ==============================================================
# 2️⃣ Conexão com o Banco Oracle
# ==============================================================
def getConnection():
    try:
        return oracledb.connect(
            user="rm559072",
            password="280305",
            dsn="oracle.fiap.com.br:1521/ORCL"
        )
    except Exception as e:
        print("❌ Erro ao conectar no Oracle:", e)
        raise


# ==============================================================
# 3️⃣ Página inicial (Render vai usar isso)
# ==============================================================
@app.route("/")
def home():
    return render_template("index.html")


# ==============================================================
# 4️⃣ Funções auxiliares de banco
# ==============================================================
def listar_proximas_consultas_db(cpf):
    conn = getConnection()
    cursor = conn.cursor()
    query = """
        SELECT id_consulta,
               TO_CHAR(data_consulta, 'YYYY-MM-DD HH24:MI:SS'),
               nome_medico,
               presenca
        FROM consultas
        WHERE cpf_paciente = :cpf
        ORDER BY data_consulta
    """
    cursor.execute(query, [cpf])
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def confirmar_consulta_db(cpf, id_consulta):
    conn = getConnection()
    cursor = conn.cursor()
    query = """
        UPDATE consultas
        SET presenca = 'Confirmada'
        WHERE cpf_paciente = :cpf AND id_consulta = :id
    """
    cursor.execute(query, [cpf, id_consulta])
    conn.commit()
    cursor.close()
    conn.close()


def cancelar_consulta_db(cpf, id_consulta):
    conn = getConnection()
    cursor = conn.cursor()
    query = """
        UPDATE consultas
        SET presenca = 'Cancelada'
        WHERE cpf_paciente = :cpf AND id_consulta = :id
    """
    cursor.execute(query, [cpf, id_consulta])
    conn.commit()
    cursor.close()
    conn.close()


def listar_observacoes_db(cpf, id_consulta):
    conn = getConnection()
    cursor = conn.cursor()
    query = """
        SELECT texto_observacao, TO_CHAR(data_obs, 'YYYY-MM-DD HH24:MI:SS')
        FROM observacoes
        WHERE cpf_paciente = :cpf AND id_consulta = :id
        ORDER BY data_obs DESC
    """
    cursor.execute(query, [cpf, id_consulta])
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def adicionar_observacao_db(cpf, id_consulta, texto):
    conn = getConnection()
    cursor = conn.cursor()
    query = """
        INSERT INTO observacoes (id_obs, cpf_paciente, id_consulta, texto_observacao, data_obs)
        VALUES (obs_seq.NEXTVAL, :cpf, :id, :texto, SYSDATE)
    """
    cursor.execute(query, [cpf, id_consulta, texto])
    conn.commit()
    cursor.close()
    conn.close()


# ==============================================================
# 5️⃣ Rotas da API
# ==============================================================

# 🔹 Listar consultas
@app.route("/consultas/<cpf>", methods=["GET"])
def api_listar_consultas(cpf):
    try:
        consultas = listar_proximas_consultas_db(cpf)
        consultas_json = [
            {
                "id": c[0],
                "data": c[1],
                "medico": c[2],
                "status": c[3] if c[3] else "Pendente"
            }
            for c in consultas
        ]
        return jsonify(consultas_json)
    except Exception as e:
        print("❌ Erro ao buscar consultas:", e)
        return jsonify({"erro": str(e)}), 500


# 🔹 Confirmar consulta
@app.route("/consultas/confirmar", methods=["POST"])
def api_confirmar_consulta():
    dados = request.get_json()
    try:
        confirmar_consulta_db(dados["cpf"], dados["id_consulta"])
        return jsonify({"mensagem": "Consulta confirmada com sucesso!"})
    except Exception as e:
        print("❌ Erro ao confirmar consulta:", e)
        return jsonify({"erro": str(e)}), 500


# 🔹 Cancelar consulta
@app.route("/consultas/cancelar", methods=["POST"])
def api_cancelar_consulta():
    dados = request.get_json()
    try:
        cancelar_consulta_db(dados["cpf"], dados["id_consulta"])
        return jsonify({"mensagem": "Consulta cancelada com sucesso!"})
    except Exception as e:
        print("❌ Erro ao cancelar consulta:", e)
        return jsonify({"erro": str(e)}), 500


# 🔹 Listar observações
@app.route("/observacoes/<cpf>/<int:id_consulta>", methods=["GET"])
def api_listar_observacoes(cpf, id_consulta):
    try:
        obs = listar_observacoes_db(cpf, id_consulta)
        obs_json = [
            {"texto": o[0], "data": o[1]} for o in obs
        ]
        return jsonify(obs_json)
    except Exception as e:
        print("❌ Erro ao buscar observações:", e)
        return jsonify({"erro": str(e)}), 500


# 🔹 Adicionar observação
@app.route("/observacoes/adicionar", methods=["POST"])
def api_adicionar_observacao():
    dados = request.get_json()
    try:
        adicionar_observacao_db(dados["cpf"], dados["id_consulta"], dados["texto"])
        return jsonify({"mensagem": "Observação adicionada com sucesso!"})
    except Exception as e:
        print("❌ Erro ao adicionar observação:", e)
        return jsonify({"erro": str(e)}), 500


# ==============================================================
# 6️⃣ Executar servidor
# ==============================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
