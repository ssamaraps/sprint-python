# ==============================================================
# resetar_banco.py
# Script para apagar as tabelas do projeto "Assistente Virtual HC"
# ==============================================================
# ⚠️ Atenção: Este código APAGA as tabelas e todos os dados contidos nelas.
# Use apenas se tiver certeza de que deseja reiniciar o banco de dados.
# ==============================================================

import oracledb

# ==============================
# Função de Conexão com o Banco
# ==============================
def getConnection():
    """Realiza a conexão com o banco de dados Oracle"""
    try:
        conn = oracledb.connect(
            user="rm559072",             # mesmo usuário usado no projeto principal
            password="130106",           # mesma senha
            host="oracle.fiap.com.br",
            port=1521,
            service_name="orcl"
        )
        print("✅ Conexão feita com sucesso!")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {e}")
        return None

# ==============================
# Função para Apagar Tabelas
# ==============================
def apagar_tabelas():
    """Apaga as tabelas do projeto (pacientes_hc, consultas e observacoes)"""
    conn = getConnection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()

        # Lista das tabelas que queremos apagar
        tabelas = ["observacoes", "consultas", "pacientes_hc"]  # ordem importa por causa das FK

        for tabela in tabelas:
            try:
                cursor.execute(f"DROP TABLE {tabela} CASCADE CONSTRAINTS")
                print(f"✅ Tabela '{tabela}' apagada com sucesso!")
            except oracledb.Error as e:
                # Caso a tabela não exista, apenas exibe o aviso e continua
                if "ORA-00942" in str(e):
                    print(f"⚠️ Tabela '{tabela}' não existe, pulando...")
                else:
                    print(f"❌ Erro ao apagar '{tabela}': {e}")

        conn.commit()
        print("\n💾 Banco de dados resetado com sucesso!")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        conn.rollback()
    finally:
        conn.close()

# ==============================
# Execução Principal
# ==============================
if __name__ == "__main__":
    print("=== RESETAR BANCO DE DADOS - ASSISTENTE HC ===")
    confirmacao = input("Tem certeza que deseja apagar TODAS as tabelas? (s/n): ").strip().lower()
    
    if confirmacao == "s":
        apagar_tabelas()
    else:
        print("❌ Operação cancelada pelo usuário.")
