# ==============================================================  
# vcreate.py - Script de Criação de Tabelas Refatorado  
# ==============================================================  

import oracledb

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
        print(f"❌ Erro ao conectar: {e}")
        return None

def criar_tabelas():
    conn = getConnection()
    if not conn:
        return
    try:
        cursor = conn.cursor()

        # Tabela de pacientes
        cursor.execute("""
            CREATE TABLE pacientes_hc(
                id_paciente NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                nome_paciente VARCHAR2(50),
                sobrenome_paciente VARCHAR2(50),
                idade NUMBER(3),
                cpf_paciente VARCHAR2(11) UNIQUE,
                tipo_reabilitacao VARCHAR2(20),
                cep VARCHAR2(9),
                logradouro VARCHAR2(100),
                bairro VARCHAR2(50),
                cidade VARCHAR2(50),
                uf VARCHAR2(2)
            )
        """)

        # Tabela de consultas (usando TIMESTAMP para data + hora)
        cursor.execute("""
            CREATE TABLE consultas(
                id_consulta NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                data_consulta TIMESTAMP,
                cpf_paciente VARCHAR2(11),
                nome_medico VARCHAR2(50),
                presenca VARCHAR2(20),
                FOREIGN KEY (cpf_paciente) REFERENCES pacientes_hc(cpf_paciente)
            )
        """)

        # Tabela de observações
        cursor.execute("""
            CREATE TABLE observacoes(
                id_observacao NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                cpf_paciente VARCHAR2(11) NOT NULL,
                id_consulta NUMBER NOT NULL,
                descricao VARCHAR2(4000),
                data_criacao DATE DEFAULT SYSDATE,
                CONSTRAINT fk_obs_paciente FOREIGN KEY (cpf_paciente) REFERENCES pacientes_hc(cpf_paciente),
                CONSTRAINT fk_obs_consulta FOREIGN KEY (id_consulta) REFERENCES consultas(id_consulta)
            )
        """)

        conn.commit()
        print("✅ Tabelas criadas com sucesso!")
    except oracledb.Error as e:
        if "ORA-00955" in str(e):
            print("⚠️ As tabelas já existem.")
        else:
            print(f"Erro ao criar tabelas: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    criar_tabelas()
