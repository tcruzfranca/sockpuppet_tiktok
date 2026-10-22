"""
Projeto acadêmico de auditoria de mecanismos de recomendação.

Autores:
    Tiago Cruz de França
    Jonice Oliveira
    Daniel Sadoc
    Eduardo Hargreaves

Programador:
    Tiago Cruz de França

Uso restrito aos fins autorizados pelos autores.
"""

import asyncio
from typing import Optional
from playwright.async_api import async_playwright
from SockpuppetConfig import SockpuppetConfig

# ==============================================================================
# CONFIGURAÇÕES DO SOCK PUPPET
# ==============================================================================
# Define a pasta local onde os dados da seção do navegador, o arquivo com as configurações da sessão
# e a pasta onde serão mantidos os snapshots com as impressions (feeds) da timeline.
config: Optional[SockpuppetConfig] = None
# ==============================================================================

def setup_sockpuppet_standalone_vars():
    global config #SOCK_PUPPET_NAME, SOCK_PUPPET_DIR, SESSION_FILE
    config = SockpuppetConfig()

    print("O nome que você der será usado para: \n\t-pasta com dados de navegação, \n\t-arquivo json com sessão e \n\tarquivos de snapshots da timeline.")
    print("Inicie com letras e use apenas letras e números.")
    config.sockpuppet_name = input("Nomeie do sockpuppet-audit: ")
    config.sockpuppet_dir += config.sockpuppet_name
    config.session_file += config.sockpuppet_name+".json"

def setup_sockpuppet_vars(configParam: SockpuppetConfig): #sock_name,sock_navegador_dir,sock_session_file_name):

    global config
    config = configParam

async def setup_sockpuppet_session():
    async with async_playwright() as p:
        print(f"Iniciando o Chrome com a pasta de perfil isolada: '{config.sockpuppet_dir}'...")

        # O Playwright criará a pasta SOCK_PUPPET_DIR automaticamente se ela não existir
        context = await p.chromium.launch_persistent_context(
            user_data_dir=config.sockpuppet_dir,
            channel="chrome",  # Usa o binário do Chrome instalado no sistema
            headless=False,    # Deve ser False para você conseguir interagir no login
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )

        page = context.pages[0] if context.pages else await context.new_page()
        
        print("Navegando para a página de login do TikTok...")
        await page.goto("https://www.tiktok.com/login")

        print("\n" + "="*70)
        print("AÇÃO MANUAL NECESSÁRIA:")
        print("1. Na janela do Chrome que abriu, faça o login na conta do TikTok/Google.")
        print("2. Resolva eventuais CAPTCHAs ou verificações de segurança.")
        print("3. Quando estiver vendo o feed 'Para Você' ou a página inicial logada:")
        print("   Volte aqui no terminal e pressione ENTER.")
        print("="*70 + "\n")

        input("Pressione ENTER após concluir o login no navegador...")

        # Exporta o arquivo de estado de sessão como backup (opcional, mas recomendado)
        await context.storage_state(path=config.session_file)
        print(f"Sessão salva com sucesso em '{config.session_file}'!")
        print(f"Todos os dados do perfil permanecem gravados em '{config.sockpuppet_dir}'.")

        await context.close()

if __name__ == "__main__":
    print("Você está executando o loginSockTikTok.py de forma isolada. Dê preferência a rodar o pipeline.")
    print("Para isso, para isso, interrompa este script e acesse sockpuppetRun.py.")
    interromper = input("Interromper (S) ou Não (n)? ")

    if (interromper == "n"):
        setup_sockpuppet_standalone_vars()
        asyncio.run(setup_sockpuppet_session())
    else:
        print("Finalizando sem rodar o script!")
