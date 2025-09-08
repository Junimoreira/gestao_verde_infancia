import streamlit as st
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# ========================================================
# 🔹 Carregar variáveis de ambiente
# ========================================================
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ========================================================
# 🔹 Configuração da página
# ========================================================
st.set_page_config(page_title="Gestão Verde Infância", layout="wide")

# ========================================================
# 🔹 CSS customizado
# ========================================================
st.markdown(
    """
    <style>
        .stApp {
            background-image: url("logo_verde_infancia.png");
            background-size: 30%;
            background-repeat: no-repeat;
            background-position: top right;
            background-attachment: fixed;
        }
        div.stButton > button {
            background-color: #44d62c;
            color: white;
            border-radius: 10px;
            border: none;
            font-weight: bold;
        }
        div.stButton > button:hover {
            background-color: #0080acd;
            color: white;
        }
        h1, h2, h3 {
            color: #0080acd;
        }
        section[data-testid="stSidebar"] {
            background-color: #f2fdf1;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ========================================================
# 🔹 Controle de sessão
# ========================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "pagina" not in st.session_state:
    st.session_state.pagina = None

# ========================================================
# 🔹 Login
# ========================================================
if not st.session_state.autenticado:
    st.title("🔑 Login - Gestão Verde Infância")

    with st.form("login_form"):
        email_login = st.text_input("Email")
        senha_login = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if submitted:
            try:
                res = supabase.table("usuarios").select("*").eq("email", email_login).eq("senha", senha_login).execute()
                if res.data:
                    st.session_state.autenticado = True
                    st.session_state.usuario = res.data[0]
                    st.session_state.pagina = "Clientes"  # 👉 entra direto em Clientes
                    st.success(f"✅ Bem-vindo, {st.session_state.usuario['email']}!")
                    st.rerun()
                else:
                    st.error("⚠️ Usuário ou senha inválidos.")
            except Exception as e:
                st.error(f"Erro ao autenticar: {e}")

else:
    # ========================================================
    # 🔹 Info do usuário logado
    # ========================================================
    role = st.session_state.usuario.get("role", "user")
    st.sidebar.markdown(f"👋 **Logado como:** {st.session_state.usuario['email']} ({role})")

    # ========================================================
    # 🔹 Menu principal com botões
    # ========================================================
    st.sidebar.title("📌 Menu")
    if st.sidebar.button("📋 Clientes"):
        st.session_state.pagina = "Clientes"
    if st.sidebar.button("📦 Produtos"):
        st.session_state.pagina = "Produtos"
    if role == "admin":  # 👉 só admin vê a aba Usuários
        if st.sidebar.button("👤 Usuários"):
            st.session_state.pagina = "Usuários"
    if st.sidebar.button("🚪 Logout"):
        st.session_state.autenticado = False
        st.session_state.usuario = None
        st.session_state.pagina = None
        st.rerun()

    # ========================================================
    # 🔹 Conteúdo das páginas
    # ========================================================
    if st.session_state.pagina == "Usuários" and role == "admin":
        st.title("👤 Gerenciar Usuários")

        with st.form("form_usuario"):
            id_usuario = st.text_input("ID (opcional, se já existir)", key="id_usuario")
            email = st.text_input("Email", key="email_usuario")
            senha = st.text_input("Senha", type="password", key="senha_usuario")
            role_form = st.selectbox("Papel", ["user", "admin"], key="role_usuario")
            submitted = st.form_submit_button("Cadastrar Usuário")

            if submitted:
                try:
                    existe = supabase.table("usuarios").select("*").eq("email", email).execute()
                    if existe.data:
                        st.error("⚠️ Usuário já existe!")
                    else:
                        supabase.table("usuarios").insert({
                            "id": id_usuario if id_usuario else None,
                            "email": email,
                            "senha": senha,
                            "role": role_form
                        }).execute()
                        st.success(f"✅ Usuário {email} cadastrado com sucesso!")

                        st.session_state.id_usuario = ""
                        st.session_state.email_usuario = ""
                        st.session_state.senha_usuario = ""
                        st.session_state.role_usuario = "user"
                except Exception as e:
                    st.error(f"Erro: {e}")

        st.subheader("📑 Lista de Usuários")
        usuarios = supabase.table("usuarios").select("*").execute()
        if usuarios.data:
            st.dataframe(pd.DataFrame(usuarios.data))
        else:
            st.info("Nenhum usuário cadastrado ainda.")

    elif st.session_state.pagina == "Clientes":
        st.title("📋 Cadastro de Clientes")

        with st.form("form_cliente"):
            nome = st.text_input("Nome do Cliente", key="nome_cliente")
            telefone = st.text_input("Telefone", key="tel_cliente")
            email = st.text_input("Email", key="email_cliente")
            submitted = st.form_submit_button("Cadastrar Cliente")

            if submitted:
                try:
                    supabase.table("clientes").insert({
                        "nome": nome,
                        "telefone": telefone,
                        "email": email
                    }).execute()
                    st.success(f"✅ Cliente {nome} cadastrado com sucesso!")

                    st.session_state.nome_cliente = ""
                    st.session_state.tel_cliente = ""
                    st.session_state.email_cliente = ""
                except Exception as e:
                    st.error(f"Erro: {e}")

        st.subheader("📑 Lista de Clientes")
        clientes = supabase.table("clientes").select("*").execute()
        if clientes.data:
            st.dataframe(pd.DataFrame(clientes.data))
        else:
            st.info("Nenhum cliente cadastrado ainda.")

    elif st.session_state.pagina == "Produtos":
        st.title("📦 Cadastro de Produtos")

        st.subheader("➕ Cadastro Manual")
        with st.form("form_produto"):
            codigo_barras = st.text_input("Código de Barras", key="cb_prod")
            codigo = st.text_input("Código Interno", key="cod_prod")
            descricao = st.text_input("Descrição", key="desc_prod")
            quantidade = st.number_input("Quantidade", min_value=1, value=1, key="qtde_prod")
            valor = st.number_input("Valor Unitário (R$)", min_value=0.0, format="%.2f", key="valor_prod")
            user_id = st.text_input("ID Usuário Responsável", key="uid_prod")
            submitted = st.form_submit_button("Cadastrar Produto")

            if submitted:
                valor_total = quantidade * valor
                try:
                    supabase.table("produtos").insert({
                        "codigo_barras": codigo_barras,
                        "codigo": codigo,
                        "descricao": descricao,
                        "quantidade": quantidade,
                        "valor": valor,
                        "valor_total": valor_total,
                        "user_id": user_id
                    }).execute()
                    st.success(f"✅ Produto {descricao} cadastrado com sucesso!")

                    st.session_state.cb_prod = ""
                    st.session_state.cod_prod = ""
                    st.session_state.desc_prod = ""
                    st.session_state.qtde_prod = 1
                    st.session_state.valor_prod = 0.0
                    st.session_state.uid_prod = ""
                except Exception as e:
                    st.error(f"Erro: {e}")

        st.subheader("📂 Importar Produtos via Excel")
        arquivo = st.file_uploader("Selecione um arquivo Excel (.xlsx ou .xls)", type=["xlsx", "xls"])
        if arquivo is not None:
            try:
                df = pd.read_excel(arquivo)
                st.write("Pré-visualização dos dados:")
                st.dataframe(df.head())

                if st.button("Importar para o Supabase"):
                    registros = df.to_dict(orient="records")
                    for r in registros:
                        r["valor_total"] = r["quantidade"] * r["valor"]
                    supabase.table("produtos").insert(registros).execute()
                    st.success("✅ Produtos importados com sucesso!")
            except Exception as e:
                st.error(f"Erro ao importar: {e}")

        st.subheader("📑 Lista de Produtos")
        produtos = supabase.table("produtos").select("*").execute()
        if produtos.data:
            st.dataframe(pd.DataFrame(produtos.data))
        else:
            st.info("Nenhum produto cadastrado ainda.")
