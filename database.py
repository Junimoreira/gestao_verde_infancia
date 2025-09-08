import sqlite3

# Criar conexão
def conectar():
    return sqlite3.connect("clientes.db")

# Criar tabela se não existir
def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Inserir cliente
def inserir_cliente(nome, telefone):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nome, telefone) VALUES (?, ?)", (nome, telefone))
    conn.commit()
    conn.close()

# Listar clientes
def listar_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    dados = cursor.fetchall()
    conn.close()
    return dados

# Atualizar cliente
def atualizar_cliente(cliente_id, nome, telefone):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE clientes SET nome=?, telefone=? WHERE id=?", (nome, telefone, cliente_id))
    conn.commit()
    conn.close()

# Excluir cliente
def excluir_cliente(cliente_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
    conn.commit()
    conn.close()