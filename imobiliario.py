import streamlit as st
import pandas as pd
import base64
import json

# Inicialize o contador de rodada no st.session_state
if "rodada" not in st.session_state:
    st.session_state.rodada = 0

# Carregar o arquivo Excel com as jogadas
df = pd.read_excel("jogadas.xlsx")

# Função para salvar o estado do jogo em um link codificado
def gerar_link_jogo(jogadores_df):
    jogo_json = jogadores_df.to_json()
    jogo_codificado = base64.b64encode(jogo_json.encode()).decode()
    return jogo_codificado

# Função para carregar o jogo a partir de um código codificado
def carregar_jogo(codigo):
    try:
        jogo_decodificado = base64.b64decode(codigo).decode()
        return pd.read_json(jogo_decodificado)
    except Exception as e:
        st.error("Erro ao importar o jogo. Verifique o código.")
        return pd.DataFrame(columns=["Nome", "Saldo", "Propriedades"])

# Inicialização
if "jogadores" not in st.session_state:
    st.session_state.jogadores = pd.DataFrame(columns=["Nome", "Saldo", "Propriedades"])

if "estado_jogo" not in st.session_state:
    st.session_state.estado_jogo = "menu"  # "menu", "jogo"

# Menu inicial
if st.session_state.estado_jogo == "menu":
    st.title("Banco Imobiliário")
    st.subheader("Escolha uma opção:")

    # Opção: Iniciar Novo Jogo
    if st.button("Iniciar Novo Jogo"):
        # Criar DataFrame de jogadores com o Banco
        st.session_state.jogadores = pd.DataFrame(columns=["Nome", "Saldo", "Propriedades"])
        banco = {"Nome": "Banco", "Saldo": 20508, "Propriedades": ""}
        st.session_state.jogadores = pd.concat(
            [st.session_state.jogadores, pd.DataFrame([banco])], ignore_index=True
        )
        st.session_state.estado_jogo = "jogo"

    # Opção: Importar Jogo
    st.write("Ou cole um código para carregar um jogo salvo:")
    codigo_importado = st.text_input("Código do Jogo")
    if st.button("Importar Jogo"):
        if codigo_importado:
            st.session_state.jogadores = carregar_jogo(codigo_importado)
            st.session_state.estado_jogo = "jogo"
        else:
            st.error("Por favor, insira um código válido.")

# Tela do jogo
elif st.session_state.estado_jogo == "jogo":
    st.title("Banco Imobiliário - Gerenciamento de Jogo")

    # Adicionar jogador
    st.sidebar.subheader("Adicionar Jogador")
    nome = st.sidebar.text_input("Nome do jogador")
    if st.sidebar.button("Adicionar Jogador"):
        if nome:
            novo_jogador = {"Nome": nome, "Saldo": 1500, "Propriedades": ""}
            st.session_state.jogadores = pd.concat(
                [st.session_state.jogadores, pd.DataFrame([novo_jogador])], ignore_index=True
            )
            st.success(f"Jogador {nome} adicionado com sucesso!")
        else:
            st.error("Por favor, insira um nome.")

    # Gerenciar transações
    st.sidebar.subheader("Atualizar Saldo")
    if not st.session_state.jogadores.empty:
        jogador_selecionado = st.sidebar.selectbox("Selecione o jogador beneficiado", st.session_state.jogadores["Nome"])
        jogador_selecionado_b = st.sidebar.selectbox("Selecione o jogador pagador", st.session_state.jogadores["Nome"])
        valor_transacao = st.sidebar.number_input("Valor da transação", step=10.0)
        
        if st.sidebar.button("Atualizar Saldo"):
            # Atualizar o saldo do jogador beneficiado
            idx = st.session_state.jogadores[st.session_state.jogadores["Nome"] == jogador_selecionado].index[0]
            st.session_state.jogadores.at[idx, "Saldo"] += valor_transacao
            
            # Atualizar o saldo do jogador pagador
            idx = st.session_state.jogadores[st.session_state.jogadores["Nome"] == jogador_selecionado_b].index[0]
            st.session_state.jogadores.at[idx, "Saldo"] -= valor_transacao

            st.success(f"Saldos de {jogador_selecionado} e {jogador_selecionado_b} atualizados com sucesso!")
            
            # Atualizar o contador de rodada
            st.session_state.rodada += 1

            # Adicionar os dados de saldo ao DataFrame df
            for jogador in st.session_state.jogadores["Nome"]:
                idx = st.session_state.jogadores[st.session_state.jogadores["Nome"] == jogador].index[0]
                saldo = st.session_state.jogadores.at[idx, "Saldo"]
                novos_dados = {'jogador': jogador, 'saldo': saldo, 'rodada': st.session_state.rodada}
                df = pd.concat([df, pd.DataFrame([novos_dados])], ignore_index=True)
            
            # Salvar os dados em um arquivo Excel, por exemplo
            df.to_excel("jogadas.xlsx", index=False)

    else:
        st.warning("Nenhum jogador adicionado.")

    # Exibir estado atual
    st.subheader("Estado Atual")
    st.dataframe(st.session_state.jogadores)

# Exibir gráfico de linha para todos os jogadores
st.subheader("Gráfico de Saldos dos Jogadores")



    # Salvar o jogo
st.subheader("Salvar Jogo")
if st.button("Gerar Código do Jogo"):
        link = gerar_link_jogo(st.session_state.jogadores)
        st.write("Compartilhe este código para carregar o jogo:")
        st.text(link)

    # Voltar ao menu inicial
if st.button("Voltar ao Menu Inicial"):
        st.session_state.estado_jogo = "menu"
