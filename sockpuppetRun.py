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
import loginSockTikTok
import sockTimeline
import seguirUsuariosSock  # Importa o novo módulo
import sys
from SockpuppetConfig import SockpuppetConfig
from pathlib import Path
from playwright.async_api import async_playwright

if sys.version_info >= (3, 11):
    import tomllib as toml_parser
    TomlError = toml_parser.TOMLDecodeError
else:
    import toml as toml_parser
    TomlError = toml_parser.TomlDecodeError


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
            # Leitura com modo "rb"
            with open(config_path, "rb") as f:
                dados_config = toml_parser.load(f)
        else:
            dados_config = {}

        # 2. Modifica os valores das chaves que você deseja alterar
        # (As outras chaves e comentários que você não mexer continuarão iguais)
        dados_config["sockpuppet_name"] = config.sockpuppet_name
        dados_config["snapshots_dir"] = config.snapshots_dir
        dados_config["sockpuppet_dir"] = config.sockpuppet_dir
        dados_config["session_file"] = config.session_file
        dados_config["orientacao"] = config.orientacao if config.orientacao in ORIENTACOES_VALIDAS else "neutro"
        
        # SALVA O CAMPO PARTIDOS NO ARCHIVO TOML
        dados_config["partidos"] = config.partidos

        dados_config["quantidade_intervalos_dormindo"] = config.quantidade_intervalos_dormindo
        dados_config["intervalos_em_segundos"] = config.intervalos_em_segundos

        # 3. Abre o arquivo em modo de escrita ('w') e salva as alterações
        import toml as toml_writer
        with open(config_path, "w", encoding="utf-8") as f:
            toml_writer.dump(dados_config, f)
        result = True
        print("Arquivo config.toml atualizado com sucesso!")
    else:
        print("config.toml só pode ser atulizado quando os dados de SockpuppetConfig estiverem disponíveis.")

    return result



def configure_main_var_names(caminho_arquivo="config.toml"):

    global config
    result = False

    if (config.sockpuppet_name != ""):
        config.snapshots_dir += config.sockpuppet_name
        config.sockpuppet_dir += config.sockpuppet_name
        config.session_file += config.sockpuppet_name + ".json"

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

    # =========================================================================
    # NOVA ETAPA: DEFINIÇÃO DOS PARTIDOS
    # =========================================================================
    default_partidos = config.partidos.strip().lower() if config.partidos else ""
    prompt_partidos = f"[{default_partidos}]" if default_partidos else "[vazio/todos]"
    
    entrada_partidos = input(f"Informe o(s) partido(s) de interesse (ex: 'pt', 'pl', 'pt,pl') ou ENTER para manter {prompt_partidos}: ").strip().lower()

    if entrada_partidos != "":
        config.partidos = entrada_partidos
    else:
        config.partidos = default_partidos

    print(f"[✓] Partido(s) definido(s) como: '{config.partidos}'")

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
    result = False

    if Path(caminho_arquivo).exists():
        try:
            # "rb" é aceito e exigido pelo tomllib e aceito pelo toml antigo
            with open(caminho_arquivo, "rb") as f:
                dados_from_config_toml = toml_parser.load(f)

            if "sockpuppet_name" in dados_from_config_toml:
                config.sockpuppet_name = dados_from_config_toml["sockpuppet_name"]
            if "snapshots_dir" in dados_from_config_toml:
                config.snapshots_dir = dados_from_config_toml["snapshots_dir"]
            if "sockpuppet_dir" in dados_from_config_toml:
                config.sockpuppet_dir = dados_from_config_toml["sockpuppet_dir"]
            if "session_file" in dados_from_config_toml:
                config.session_file = dados_from_config_toml["session_file"]
            if "orientacao" in dados_from_config_toml:
                config.orientacao = dados_from_config_toml["orientacao"]
            if "partidos" in dados_from_config_toml:
                config.partidos = dados_from_config_toml["partidos"]
            if "seguindo_usuarios_concluido" in dados_from_config_toml:
                config.seguindo_usuarios_concluido = dados_from_config_toml["seguindo_usuarios_concluido"]

            result = True

        except TomlError:
            print(f"Erro de sintaxe no arquivo de configuração TOML: {caminho_arquivo}")
        except Exception as e:
            print(f"Erro ao carregar o arquivo de configuração: {e}")
    else:
        print(f"Arquivo de configuração não encontrado: {caminho_arquivo}")

    return result


def config_environment_using_session_file(caminho_arquivo = "config.toml"):
    # Cria um gerador que busca arquivos .json no diretório atual ('.')
    arquivo_json = list(Path('.').glob('tiktok_session_*.json'))

    result = False

    if arquivo_json:
        print(f"Esse diretório já tem a configuração de um sockpuppet!")
        result = True

        nome_arquivo = arquivo_json[0]
        sock_name = nome_arquivo.name
        sock_name = sock_name.replace("tiktok_session_","")
        sock_name = sock_name.replace(".json","")
        config.sockpuppet_name = sock_name
        result = configure_main_var_names()
        
        '''
        #tem algo errado, existe mais de um arquivo .json neste diretório        
        if (len(arquivo_json) > 1):                    
            print("Inconsistência no diretório. Diferentes arquivos tiktok_session_*.json")            
            print("Nomes encontrados:")
            # Exibe o nome de cada arquivo encontrado
            for arquivo in arquivo_json:
                print(arquivo.name)

            is_dir_existis(config.snapshots_dir)
            is_dir_existis(config.sockpuppet_dir)
         '''
    else:
        print("Iniciaremos a configuração do ambiente.")
    
    return result


def is_sockpuppet_environment_configured():

    result = config_environment_using_config_file("config.toml")

    if (not result):
        result = config_environment_using_session_file("config.toml")

    return result


def is_sessao_valida() -> bool:
    """
    Verifica se a pasta de dados do perfil do navegador ou o arquivo de sessão
    existem e possuem conteúdo, garantindo que o sockpuppet tem uma sessão ativa.
    """
    global config

    caminho_dir = Path(config.sockpuppet_dir)
    caminho_json = Path(config.session_file)

    # Verifica se o diretório do navegador existe e não está vazio
    dir_valido = caminho_dir.exists() and any(caminho_dir.iterdir())
    
    # Verifica se o arquivo .json de sessão existe
    json_valido = caminho_json.exists() and caminho_json.stat().st_size > 0

    if not (dir_valido or json_valido):
        print("\n" + "!" * 80)
        print(" [ERRO DE SESSÃO] Nenhuma sessão válida encontrada para este Sockpuppet!")
        print(f" Diretório esperado: {config.sockpuppet_dir}")
        print(f" Arquivo de sessão esperado: {config.session_file}")
        print(" [AÇÃO] Execute o setup inicial de login para autenticar o perfil.")
        print("!" * 80 + "\n")
        return False

    return True


async def verificar_login_ativo() -> bool:
    """
    Acessa o TikTok e verifica se existe uma sessão autenticada ativa,
    checando a presença de cookies de sessão e elementos do DOM pós-login.
    """
    if not config or not config.sockpuppet_dir:
        return False

    print("[+] Verificando se a sessão do TikTok está autenticada...")

    async with async_playwright() as p:
        try:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=config.sockpuppet_dir,
                channel="chrome",
                headless=True,  # Checagem silenciosa em segundo plano
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )

            page = context.pages[0] if context.pages else await context.new_page()
            
            # 1. Checa a presença dos cookies essenciais de sessão no context
            cookies = await context.cookies("https://www.tiktok.com")
            nomes_cookies = [c["name"] for c in cookies]
            tem_cookie_sessao = any(name in nomes_cookies for name in ["sessionid", "sessionid_ss", "sid_tt", "sid_guard"])

            if not tem_cookie_sessao:
                print("[-] Nenhum cookie de autenticação (sessionid) foi localizado no perfil.")
                await context.close()
                return False

            # 2. Confirma a sessão acessando a Home do TikTok
            await page.goto("https://www.tiktok.com/foryou", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3.0)

            # 3. Busca no DOM por elementos exclusivos de contas logadas
            # Ex: Avatar do perfil, menu de conta ou botão de upload de vídeo
            esta_logado = await page.evaluate("""
                () => {
                    const avatar = document.querySelector('header avatar-container, [data-e2e="profile-icon"], img[class*="avatar"]');
                    const uploadBtn = document.querySelector('a[href*="/upload"], [data-e2e="upload-icon"]');
                    const loginBtn = document.querySelector('[data-e2e="top-login-button"]');
                    
                    // Se o botão de login NÃO estiver visível e existir avatar/upload, o login está ativo
                    if (loginBtn && loginBtn.offsetWidth > 0 && loginBtn.offsetHeight > 0) {
                        return false;
                    }
                    return (avatar !== null || uploadBtn !== null);
                }
            """)

            await context.close()

            if esta_logado:
                print("[✓] Login no TikTok confirmado e ativo!")
                return True
            else:
                print("[-] A página carregou, mas a conta parece estar deslogada.")
                return False

        except Exception as e:
            print(f"[-] Erro ao verificar estado do login: {e}")
            return False


if __name__ == "__main__":

    # 1. Carrega e valida a configuração básica do ambiente (.toml ou .json)
    if (not is_sockpuppet_environment_configured()):
        print("Configurando o ambiente do sockpuppet-audit.")
        
        if (setup_sockpuppet_login()):
            loginSockTikTok.setup_sockpuppet_vars(config)
            asyncio.run(loginSockTikTok.setup_sockpuppet_session())
        else:
            raise ValueError("Erro de configuração do sockpuppet durante o login")

    # 2. TRAVA DE SEGURANÇA E REDIRECIONAMENTO DE LOGIN
    loginSockTikTok.setup_sockpuppet_vars(config)
    sessao_ativa = asyncio.run(verificar_login_ativo())

    if not sessao_ativa:
        print("\n" + "!" * 80)
        print(" [SESSÃO NÃO ENCONTRADA OU EXPIRADA] Sockpuppet deslogado do TikTok.")
        print(" [AÇÃO] Abrindo a janela do navegador para realizar a autenticação...")
        print("!" * 80 + "\n")
        
        # Redireciona para a rotina de login
        asyncio.run(loginSockTikTok.setup_sockpuppet_session())
        
        # Revalida após a tentativa de login
        if not asyncio.run(verificar_login_ativo()):
            print("[-] Falha na autenticação. Encerrando execução.")
            exit(1)

    # 3. Executa a etapa de SEGUIR OS PERFIS (caso pendente)
    if not getattr(config, "seguindo_usuarios_concluido", False):
        seguirUsuariosSock.setup_sockpuppet_vars(config)
        asyncio.run(seguirUsuariosSock.executar_seguir_usuarios())

    # 4. Dispara a coleta em loop na timeline
    # Atualiza variáveis globais e dispara a coleta em loop
    sockTimeline.setup_sockpuppet_vars(config)
    asyncio.run(sockTimeline.setup_sockpuppet_in_loop())

