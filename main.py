# ==============================================================  
# main.py - Sistema de Apoio para Teleconsultas Refatorado  
# ==============================================================  

import oracledb
import json
from datetime import date
from api import buscar_endereco_por_cep

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
        print(f'❌ Erro ao obter a conexão: {e}')
        return None

# ==============================  
# Funções de Validação
# ==============================  
def validar_cpf(cpf):
    return len(cpf) == 11 and cpf.isdigit()

def validar_idade(idade):
    return idade.isdigit() and int(idade) > 0

def validar_tipo(tipo):
    tipos_validos = ["motora", "cognitiva", "física", "ocupacional"]
    return tipo.lower() in tipos_validos

# ==============================  
# CRUD de Pacientes
# ==============================  
def create_paciente(nome, sobrenome, idade, cpf, tipo_reabilitacao, cep):
    conn = getConnection()
    if not conn: return
    endereco = buscar_endereco_por_cep(cep)
    if not endereco:
        print("⚠️ Endereço não encontrado. Verifique o CEP.")
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pacientes_hc
            (nome_paciente, sobrenome_paciente, idade, cpf_paciente, tipo_reabilitacao,
             cep, logradouro, bairro, cidade, uf)
            VALUES (:nome, :sobrenome, :idade, :cpf, :tipo,
                    :cep, :logradouro, :bairro, :cidade, :uf)
        """, {'nome': nome, 'sobrenome': sobrenome, 'idade': idade,
              'cpf': cpf, 'tipo': tipo_reabilitacao, **endereco})
        conn.commit()
        print(f"\n✅ Paciente {nome} {sobrenome} cadastrado com sucesso!")
    finally:
        conn.close()

def read_pacientes():
    conn = getConnection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nome_paciente, sobrenome_paciente, idade, cpf_paciente, cidade FROM pacientes_hc ORDER BY nome_paciente")
        pacientes = cursor.fetchall()
        if not pacientes:
            print("📭 Nenhum paciente cadastrado.")
        else:
            print("\n=== Lista de Pacientes ===")
            for p in pacientes:
                print(f"👤 {p[0]} {p[1]} | Idade: {p[2]} | CPF: {p[3]} | Cidade: {p[4]}")
    finally:
        conn.close()

def update_paciente(cpf, nova_idade, novo_tipo):
    conn = getConnection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pacientes_hc 
            SET idade = :idade, tipo_reabilitacao = :tipo
            WHERE cpf_paciente = :cpf
        """, {'idade': nova_idade, 'tipo': novo_tipo, 'cpf': cpf})
        conn.commit()
        print(f'✅ Paciente {cpf} atualizado com sucesso!' if cursor.rowcount > 0 else '⚠️ Paciente não encontrado.')
    finally:
        conn.close()

def delete_paciente(cpf):
    conn = getConnection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pacientes_hc WHERE cpf_paciente = :cpf", {'cpf': cpf})
        conn.commit()
        print(f'🗑️ Paciente com CPF {cpf} excluído com sucesso!' if cursor.rowcount > 0 else '⚠️ Paciente não encontrado.')
    finally:
        conn.close()

# ==============================  
# CRUD de Consultas (usando apenas data_consulta TIMESTAMP)
# ==============================  
def create_consulta():
    conn = getConnection()
    if not conn: return
    try:
        cpf = input("CPF do paciente: ").strip()
        data_consulta = input("Data da consulta (AAAA-MM-DD): ").strip()
        hora_consulta = input("Hora da consulta (HH:MM): ").strip()
        nome_medico = input("Nome do médico: ").strip()

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO consultas (
                data_consulta, cpf_paciente, nome_medico, presenca
            ) VALUES (
                TO_TIMESTAMP(:data_consulta || ' ' || :hora_consulta, 'YYYY-MM-DD HH24:MI'),
                :cpf, :nome_medico, 'Agendada'
            )
        """, {
            'data_consulta': data_consulta,
            'hora_consulta': hora_consulta,  # mantém para exibição
            'cpf': cpf,
            'nome_medico': nome_medico
        })
        conn.commit()
        print(f"✅ Consulta cadastrada para {cpf} em {data_consulta} às {hora_consulta}.")
    finally:
        conn.close()

def confirmar_consulta():
    conn = getConnection()
    if not conn: return
    try:
        id_consulta = input("ID da consulta: ").strip()
        cursor = conn.cursor()
        cursor.execute("UPDATE consultas SET presenca = 'Confirmada' WHERE id_consulta = :id", {'id': id_consulta})
        conn.commit()
        print("✅ Consulta confirmada!" if cursor.rowcount > 0 else "⚠️ Consulta não encontrada.")
    finally:
        conn.close()

def cancelar_consulta():
    conn = getConnection()
    if not conn: return
    try:
        id_consulta = input("ID da consulta: ").strip()
        cursor = conn.cursor()
        cursor.execute("UPDATE consultas SET presenca = 'Cancelada' WHERE id_consulta = :id", {'id': id_consulta})
        conn.commit()
        print("❌ Consulta cancelada!" if cursor.rowcount > 0 else "⚠️ Consulta não encontrada.")
    finally:
        conn.close()

def exportar_consultas_json():
    conn = getConnection()
    if not conn: return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM (
                SELECT * FROM consultas ORDER BY data_consulta DESC
            ) WHERE ROWNUM <= 10
        """)
        consultas = [
            {
                "id_consulta": r[0],
                "data_consulta": str(r[1].date()) if r[1] else "",
                "hora_consulta": r[1].strftime("%H:%M") if r[1] else "",
                "cpf_paciente": r[2],
                "nome_medico": r[3],
                "presenca": r[4]
            } for r in cursor.fetchall()
        ]
        with open("consultas_exportadas.json", "w", encoding="utf-8") as f:
            json.dump(consultas, f, ensure_ascii=False, indent=4)
        print(f"📄 {len(consultas)} consultas exportadas para 'consultas_exportadas.json'.")
    finally:
        conn.close()

# ==============================  
# Menus
# ==============================  
def submenu_pacientes():
    while True:
        print("\n--- Menu de Pacientes ---")
        print("1. Cadastrar Paciente")
        print("2. Listar Pacientes")
        print("3. Atualizar Paciente")
        print("4. Excluir Paciente")
        print("5. Voltar")
        op = input("Escolha: ").strip()
        if op == '1':
            nome = input("Nome: "); sobrenome = input("Sobrenome: ")
            idade = input("Idade: "); cpf = input("CPF (11 dígitos): ")
            tipo = input("Tipo de reabilitação: "); cep = input("CEP: ")
            if not validar_cpf(cpf): print("CPF inválido."); continue
            if not validar_idade(idade): print("Idade inválida."); continue
            create_paciente(nome, sobrenome, idade, cpf, tipo, cep)
        elif op == '2': read_pacientes()
        elif op == '3':
            cpf = input("CPF: "); idade = input("Nova idade: "); tipo = input("Novo tipo: ")
            update_paciente(cpf, idade, tipo)
        elif op == '4':
            cpf = input("CPF: "); delete_paciente(cpf)
        elif op == '5': break
        else: print("Opção inválida.")

def submenu_consultas():
    while True:
        print("\n--- Menu de Consultas ---")
        print("1. Cadastrar Consulta")
        print("2. Confirmar Consulta")
        print("3. Cancelar Consulta")
        print("4. Voltar")
        op = input("Escolha: ").strip()
        if op == '1': create_consulta()
        elif op == '2': confirmar_consulta()
        elif op == '3': cancelar_consulta()
        elif op == '4': break
        else: print("Opção inválida.")

def menu_principal():
    while True:
        print("\n=== Assistente Virtual HC ===")
        print("1. Gerenciar Pacientes")
        print("2. Gerenciar Consultas")
        print("3. Exportar Consultas JSON")
        print("4. Sair")
        escolha = input("Escolha: ").strip()
        if escolha == '1': submenu_pacientes()
        elif escolha == '2': submenu_consultas()
        elif escolha == '3': exportar_consultas_json()
        elif escolha == '4': break
        else: print("Opção inválida.")

if __name__ == "__main__":
    menu_principal()
