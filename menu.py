import json
from datetime import datetime

# Nome do arquivo onde os dados serão salvos
ARQUIVO_DADOS = 'dados_almoxarifado.json'

# Dados padrão (caso o arquivo ainda não exista ou esteja corrompido)
ESTOQUE_PADRAO = {
    "Parafusos e Fixadores": {"parafuso": 100, "prego": 150, "gancho": 50},
    "Ferramentas": {"martelo": 10, "chave de fenda": 15},
    "EPIs": {"capacete": 20, "luva": 40}
}
HISTORICO_PADRAO = []

estoque = ESTOQUE_PADRAO.copy()
historico = HISTORICO_PADRAO.copy()


def carregar_dados():
    """Carrega os dados do arquivo ou cria um novo se não existir ou estiver vazio."""
    global estoque, historico
    try:
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            # Garante que se o arquivo estiver vazio ({}), ele assume os padrões
            estoque = dados.get("estoque", ESTOQUE_PADRAO)
            historico = dados.get("historico", HISTORICO_PADRAO)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existir ou estiver corrompido/vazio, recria com o padrão
        estoque = ESTOQUE_PADRAO.copy()
        historico = HISTORICO_PADRAO.copy()
        salvar_dados()


def salvar_dados():
    """Salva o estoque e o histórico no arquivo JSON."""
    dados = {
        "estoque": estoque,
        "historico": historico
    }
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def realizar_login():
    """Pede o nome do usuário e garante que não fique em branco."""
    print("=== SISTEMA DE CONTROLE DE ESTOQUE - ALMOXARIFADO ===")
    while True:
        nome = input("Digite o seu nome de usuário: ").strip()
        if nome:
            print(f"\nBem-vindo(a), {nome}! Acesso liberado.\n")
            return nome
        else:
            print("❌ Erro: O nome de usuário não pode ficar em branco. Tente novamente.\n")


def registrar_movimentacao(tipo, produto, quantidade, usuario):
    """Registra uma entrada/saída no histórico e salva no arquivo."""
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    historico.append({
        "tipo": tipo,
        "produto": produto,
        "quantidade": quantidade,
        "responsavel": usuario,
        "data": data_atual
    })
    salvar_dados()  # Salva a alteração permanentemente!


def processar_acao_produto(categoria, produto, usuario):
    """Gerencia a entrada ou saída do produto selecionado."""
    qtd_atual = estoque[categoria][produto]
    print(f"\n>> Produto Selecionado: {produto.capitalize()} (Estoque atual: {qtd_atual})")
    print("1 - Registrar Entrada (Adicionar)")
    print("2 - Registrar Saída (Retirar)")
    print("3 - Voltar para seleção de materiais")

    acao = input("Opção desejada: ").strip()

    if acao == "3":
        return

    try:
        quantidade = int(input("Informe a quantidade: "))
        if quantidade <= 0:
            print("\n❌ Erro: A quantidade deve ser maior que zero.")
            return
    except ValueError:
        print("\n❌ Erro: Digite apenas números inteiros válidos.")
        return

    if acao == "1":
        estoque[categoria][produto] += quantidade
        registrar_movimentacao("Entrada", produto, quantidade, usuario)
        print(f"\n✅ ENTRADA REGISTRADA! Novo estoque de {produto}: {estoque[categoria][produto]}")

    elif acao == "2":
        if quantidade > qtd_atual:
            print(f"\n❌ ERRO: Quantidade insuficiente em estoque! Disponível: {qtd_atual}.")
            return
        
        estoque[categoria][produto] -= quantidade
        registrar_movimentacao("Saída", produto, quantidade, usuario)
        print(f"\n✅ SAÍDA REGISTRADA! Novo estoque de {produto}: {estoque[categoria][produto]}")
    else:
        print("\n❌ Opção inválida!")


def selecionar_produto(categoria, usuario):
    """Apresenta os produtos da categoria selecionada."""
    while True:
        print(f"\n--- PRODUTOS EM '{categoria.upper()}' ---")
        produtos = list(estoque[categoria].keys())

        for i, prod in enumerate(produtos, start=1):
            qtd = estoque[categoria][prod]
            print(f"{i} - {prod.capitalize()}: {qtd} unidades")
        print("0 - Voltar às Categorias")

        opcao = input("\nSelecione o produto: ").strip()

        if opcao == "0":
            break

        if opcao.isdigit() and 1 <= int(opcao) <= len(produtos):
            produto_selecionado = produtos[int(opcao) - 1]
            processar_acao_produto(categoria, produto_selecionado, usuario)
        else:
            print("\n❌ Opção de produto inválida!")


def gerenciar_produtos(usuario):
    """Menu de navegação por categorias do estoque."""
    while True:
        print("\n--- CATEGORIAS DO ALMOXARIFADO ---")
        categorias = list(estoque.keys())

        for i, cat in enumerate(categorias, start=1):
            print(f"{i} - {cat}")
        print("0 - Voltar ao Menu Principal")

        opcao = input("\nEscolha a categoria desejada: ").strip()

        if opcao == "0":
            break

        if opcao.isdigit() and 1 <= int(opcao) <= len(categorias):
            categoria_selecionada = categorias[int(opcao) - 1]
            selecionar_produto(categoria_selecionada, usuario)
        else:
            print("\n❌ Opção de categoria inválida!")


def exibir_historico():
    """Exibe o relatório de movimentações registradas."""
    print("\n=== HISTÓRICO DE MOVIMENTAÇÕES ===")
    if not historico:
        print("Nenhuma movimentação realizada até o momento.")
        return

    for reg in historico:
        print(f"[{reg['data']}] - {reg['tipo'].upper()}: {reg['quantidade']}x '{reg['produto']}' | Resp: {reg['responsavel']}")


def menu_principal():
    """Execução principal do sistema."""
    carregar_dados()  # Carrega os dados salvos antes de iniciar
    usuario_logado = realizar_login()

    while True:
        print("\n--- MENU PRINCIPAL ---")
        print("1 - Ver Produtos / Categorias")
        print("2 - Histórico de Movimentações")
        print("3 - Sair do Sistema")

        opcao = input("\nEscolha uma opção (1-3): ").strip()

        if opcao == "1":
            gerenciar_produtos(usuario_logado)
        elif opcao == "2":
            exibir_historico()
        elif opcao == "3":
            print(f"\nSaindo do sistema... Até logo, {usuario_logado}!")
            break
        else:
            print("\n❌ Opção inválida! Tente novamente.")


# Ponto de entrada do programa
if __name__ == "__main__":
    menu_principal()