"""
Projeto acadêmico de auditoria de mecanismos de recomendação.

Autores:
    Tiago Cruz de França
    Jonice Oliveira
    Daniel Sadoc
    Eduardo Hargreaves

Programador:
    Tiago Cruz de França

Uso restrito aos fins autorizados pelos autores. Veja o README.md.
"""

import asyncio
import toml
import loginSockTikTok
import sockTimeline
import seguirUsuariosSock  # Importa o novo módulo
from SockpuppetConfig import SockpuppetConfig
from pathlib import Path


# ==============================================================================
# CONFIGURAÇÕES DO SOCK PUPPET
# ==============================================================================
# Define a pasta local onde os dados da seção do navegador, o arquivo com as configurações da sessão
# e a pasta onde serão mantidos os snapshots com as impressions (feeds) da timeline.
config = SockpuppetConfig()
ORIENTACOES_VALIDAS = ["balanceado", "direita", "esquerda", "neutro"]
# ==============================================================================

def setup_config_file_using_config_object():

    result = False
    if (config.sockpuppet_name != ""):
        # 1. Carrega o arquivo TOML existente para um dicionário Python
        config_path = config.config_file_name

        # Garante carregamento do arquivo se existir
        if Path(config_path).exists():
            dados_config = toml.load(config_path)
        else:
            dados_config = {}

        # 2. Modifica os valores das chaves que você deseja alterar
        # (As outras chaves e comentários que você não mexer continuarão iguais)
        dados_config["sockpuppet_name"] = config.sockpuppet_name
        dados_config["snapshots_dir"] = config.snapshots_dir
        dados_config["sockpuppet_dir"] = config.sockpuppet_dir
        dados_config["session_file"] = config.session_file
        dados_config["orientacao"] = config.orientacao if config.orientacao in ORIENTACOES_VALIDAS else "neutro"
        
        dados_config["quantidade_intervalos_dormindo"] = config.quantidade_intervalos_dormindo
        dados_config["intervalos_em_segundos"] = config.intervalos_em_segundos

        # 3. Abre o arquivo em modo de escrita ('w') e salva as alterações
        with open(config_path, "w", encoding="utf-8") as f:
            toml.dump(dados_config, f)
        result = True
        print("Arquivo config.toml atualizado com sucesso!")
    else:
        print("config.toml só pode ser atulizado quando os dados de SockpuppetConfig estiverem disponíveis.")

    return result



def configure_main_var_names():

    global config
    result = False

    if (config.sockpuppet_name != ""):
        config.snapshots_dir += config.sockpuppet_name
        config.sockpuppet_dir += config.sockpuppet_name
        config.session_file += config.sockpuppet_name + ".json"

        '''
            Serão mantidos os valores padrão para o arquivo de configuração e para o intervalo  de coleta.
        '''
        '''
        if((input("usar configuração padrão: (S)Sim, (n)não: ")) == "n")):
            config.config_file_name = criar_config_file()
        '''
        setup_config_file_using_config_object()

        result = True

    return result



def criar_config_file():
    
    global config

    print("Você quer usar ou nomear um arquivo de configuração específico?")
    print("O nome padrão do arquivo é config.toml. Recomendo o padrão.")

    nome = input("Dê um nome ou pressone Enter para continuar e usar o nome padrão: ")

    #se ele deixou vazio, o nome padrão será mantido.
    if (nome != ""):
        config.config_file_name = nome

def def_orientacao_sockpuppet():
    global config

    # Se já existir uma orientação definida no config.toml / SockpuppetConfig, usa ela como default.
    # Caso contrário (ou se for inválida/vazia), assume "neutro".
    default_orientacao = config.orientacao.strip().lower() if config.orientacao else "neutro"
    if default_orientacao not in ORIENTACOES_VALIDAS:
        default_orientacao = "neutro"

    print("\n------------------------------------------------")
    print(f"Orientação do Sockpuppet (Opções válidas: {', '.join(ORIENTACOES_VALIDAS)})")
    entrada = input(f"Informe a orientação ou pressione ENTER para manter o padrão [{default_orientacao}]: ").strip().lower()

    if entrada == "":
        config.orientacao = default_orientacao
    elif entrada in ORIENTACOES_VALIDAS:
        config.orientacao = entrada
    else:
        print(f"Opção inválida '{entrada}'. Mantendo orientação padrão '{default_orientacao}'.")
        config.orientacao = default_orientacao

    print(f"[✓] Orientação definida como: '{config.orientacao}'")


def def_intervalo_coleta():

    global config

    print("Defina o intervalo em segundos.")
    #dados do intervalo de coleta
    intervalos_em_segundos = input("Intervalo em segundos ou Enter para padrão de 3600s: ")
    print("Defina quantos intervalos deseja esperar.")
    quantidade_intervalos_dormindo = input("Forneça um inteiro. Enter para manter o padrão 1:")

    try:
        if (intervalos_em_segundos == ""):
            intervalos_em_segundos = 3600
        else:
            intervalos_em_segundos = int(intervalos_em_segundos)

        if (quantidade_intervalos_dormindo == ""):
            quantidade_intervalos_dormindo = 1
        else:
            quantidade_intervalos_dormindo = int(quantidade_intervalos_dormindo)

    except ValueError:
        raise ValueError("Erro: reinicie a configuração e forneça valores inteiros para os intervalos")

    config.intervalos_em_segundos = intervalos_em_segundos
    config.quantidade_intervalos_dormindo = quantidade_intervalos_dormindo



def setup_sockpuppet_login():

    print("O nome que você der será usado para: \n\t-pasta com dados de navegação, \n\t-arquivo json com sessão e \n\t-arquivos de snapshots da timeline.")
    print("Inicie com letras e use apenas letras e números.")
    config.sockpuppet_name = input("Nomeie do sockpuppet-audit: ").strip()
    
    result = configure_main_var_names()#retorna falso se o nome estiver vazio
    
    # Pergunta sobre a orientação do puppet
    def_orientacao_sockpuppet()

    if(input("Manter arquivo de configução e intervalos com valor padrão? (S)Sim ou (n)não: ") == "n"):
        criar_config_file()
        def_intervalo_coleta()
    
    if (not result):
        print("O nome do seu sockpuppet não pode ficar vazio!")
    
    return result



def is_dir_existis(dir_name):
    # Define o diretório atual
    diretorio_atual = Path('.')

    # Busca itens com o padrão e filtra usando o método .is_dir()
    pastas = [p.name for p in diretorio_atual.glob(f'*{dir_name}*') if p.is_dir()]

    if pastas:
        print(f"Pasta(s) encontrada(s): {pastas}")
    else:
        print("Nenhuma pasta correspondente foi encontrada.")


def config_environment_using_config_file(caminho_arquivo = "config.toml"):

    global config

    try:
        result = False

        dados_from_config_toml = toml.load(caminho_arquivo)
        nome = dados_from_config_toml.get("sockpuppet_name")

        if (nome != ""):
        
            config.sockpuppet_name = nome
            config.snapshots_dir = dados_from_config_toml.get("snapshots_dir")
            config.sockpuppet_dir = dados_from_config_toml.get("sockpuppet_dir")
            config.session_file = dados_from_config_toml.get("session_file")
            
            # Carrega a orientação do arquivo ou aplica "neutro" se estiver vazia/ausente
            orientacao_lida = str(dados_from_config_toml.get("orientacao", "")).strip().lower()
            if orientacao_lida in ORIENTACOES_VALIDAS:
                config.orientacao = orientacao_lida
            else:
                config.orientacao = "neutro"

            # Carrega o campo partidos e o status de seguimento do TOML
            config.partidos = dados_from_config_toml.get("partidos", "")
            config.seguindo_usuarios_concluido = dados_from_config_toml.get("seguindo_usuarios_concluido", False)

            config.quantidade_intervalos_dormindo = dados_from_config_toml.get("quantidade_intervalos_dormindo")
            config.intervalos_em_segundos = dados_from_config_toml.get("intervalos_em_segundos")
            result = True

        return result

    except FileNotFoundError:
        raise RuntimeError(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
    except toml.TomlDecodeError:
        raise ValueError(f"Erro: O arquivo '{caminho_arquivo}' está com o formato TOML inválido.")



def config_environment_using_session_file(caminho_arquivo = "config.toml"):
    # Cria um gerador que busca arquivos .json no diretório atual ('.')
    arquivo_json = list(Path('.').glob('*.json'))

    result = False

    if arquivo_json:
        print(f"Esse diretório já tem a configuração de um sockpuppet!")
        result = True

        nome_arquivo = arquivo_json[0]
        sock_name = nome_arquivo.name
        sock_name = sock_name.replace("tiktok_session_","")
        sock_name = sock_name.replace(".json","")
        config.sockpuppet_name = sock_name
        result = configure_main_var_names(caminho_arquivo)
        
        #tem algo errado, existe mais de um arquivo .json neste diretório        
        if (len(arquivo_json) > 1):                    
            print("Inconsistência no diretório. Diferentes arquivos tiktok_session_*.json")            
            print("Nomes encontrados:")
            # Exibe o nome de cada arquivo encontrado
            for arquivo in arquivo_json:
                print(arquivo.name)

            is_dir_existis(config.snapshots_dir)
            is_dir_existis(config.sockpuppet_dir)
        
    else:
        print("Iniciaremos a configuração do ambiente.")
    
    return result


def is_sockpuppet_environment_configured():

    result = config_environment_using_config_file("config.toml")

    if (not result):
        result = config_environment_using_session_file("config.toml")

    return result


if __name__ == "__main__":

    if (not is_sockpuppet_environment_configured()):
        print("Configurando o ambiente do sockpuppet-audit.")
        
        if (setup_sockpuppet_login()):
            loginSockTikTok.setup_sockpuppet_vars(config)
            asyncio.run(loginSockTikTok.setup_sockpuppet_session())
        else:
            raise ValueError("Erro de configuração do sockpuppet durante o login")

    # Executa a etapa de SEGUIR OS PERFIS (Caso ainda não tenha sido concluída)
    if not getattr(config, "seguindo_usuarios_concluido", False):
        seguirUsuariosSock.setup_sockpuppet_vars(config)
        asyncio.run(seguirUsuariosSock.executar_seguir_usuarios())

    # Atualiza variáveis globais e dispara a coleta em loop
    sockTimeline.setup_sockpuppet_vars(config)
    asyncio.run(sockTimeline.setup_sockpuppet_in_loop())

