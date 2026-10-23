"""
Módulo de ação automatizada humanizada para seguir perfis de orientação política (Versão Web).

Autores:
    Tiago Cruz de França
    Jonice Oliveira
    Daniel Sadoc
    Eduardo Hargreaves
"""

import asyncio
import random
import os
import sys
from typing import List, Optional
from playwright.async_api import async_playwright
from SockpuppetConfig import SockpuppetConfig
# Importação híbrida segura para leitura e escrita em versões distintas do python
if sys.version_info >= (3, 11):
    import tomllib as toml_parser
    TomlError = toml_parser.TOMLDecodeError
else:
    import toml as toml_parser
    TomlError = toml_parser.TomlDecodeError

import toml as toml_writer

# Para salvar o TOML mantendo compatibilidade
import toml as toml_writer

config: Optional[SockpuppetConfig] = None


def setup_sockpuppet_vars(configParam: SockpuppetConfig):
    global config
    config = configParam


def carregar_lista_usuarios_para_seguir(caminho_arquivo: str) -> List[str]:
    """Lê o arquivo usuario_partido_orientacao_tiktok.txt e extrai os handles (@usuario)."""
    usuarios = []
    if not os.path.exists(caminho_arquivo):
        print(f"[-] Arquivo de usuários para seguir '{caminho_arquivo}' não foi encontrado.")
        return []

    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        for linha in f:
            linha_limpa = linha.strip()
            if not linha_limpa or linha_limpa.startswith("#"):
                continue

            partes = [p.strip() for p in linha_limpa.replace(";", ",").split(",")]
            usuario_raw = partes[0]

            if usuario_raw.startswith("@"):
                usuario_raw = usuario_raw[1:]

            if usuario_raw and usuario_raw not in usuarios:
                usuarios.append(usuario_raw)

    return usuarios


def marcar_etapa_seguimento_como_concluida(config_file_path: str):
    """Atualiza a chave 'seguindo_usuarios_concluido = true' no config.toml."""
    try:
        if os.path.exists(config_file_path):
            
            # Leitura em modo binário "rb" (obrigatório para tomllib)
            with open(config_file_path, "rb") as f:
                dados = toml_parser.load(f)

            dados["seguindo_usuarios_concluido"] = True

            with open(config_file_path, "w", encoding="utf-8") as f:
                toml_writer.dump(dados, f)

            print("[✓] Status atualizado: 'seguindo_usuarios_concluido = true' salvo no config.toml.")
    except Exception as e:
        print(f"[-] Erro ao atualizar {config_file_path}: {e}")


async def verificar_captcha_dom(page) -> bool:
    """Verifica se há um modal de CAPTCHA/Puzzle visível no DOM."""
    elem = await page.query_selector(
        "div[class*='captcha'], div[id*='captcha'], iframe[src*='captcha'], div[class*='verify']"
    )
    return elem is not None


async def aguardar_resolucao_humana(page) -> bool:
    """Paralisa o script e aguarda até 5 minutos para que o humano resolva o puzzle na tela."""
    print("\n" + "!" * 80)
    print(" [ALERTA DE SEGURANÇA] CAPTCHA / Desafio detectado ao tentar seguir!")
    print(" [AÇÃO NECESSÁRIA] Resolva o desafio na janela do Chrome.")
    print(" [TIMEOUT] Aguardando até 5 minutos por intervenção humana...")
    print("!" * 80 + "\n")

    tempo_limite = 300  # 5 minutos
    passo_checagem = 3
    tempo_decorrido = 0

    while tempo_decorrido < tempo_limite:
        await asyncio.sleep(passo_checagem)
        tempo_decorrido += passo_checagem

        if not await verificar_captcha_dom(page):
            print("\n[✓] CAPTCHA resolvido no navegador! Retomando o processo de seguir...\n")
            await asyncio.sleep(random.uniform(4.0, 16.0))
            return True

        if tempo_decorrido % 15 == 0:
            restante = tempo_limite - tempo_decorrido
            print(f"  [Aguardando Humano] Restam {restante}s para resolver o CAPTCHA...")

    return False


async def executar_seguir_usuarios():
    global config
    if not config:
        print("[-] Configuração não carregada em seguirUsuariosSock.")
        return

    if config.seguindo_usuarios_concluido:
        print("[i] Etapa de seguir usuários já foi concluída anteriormente. Pulando...")
        return

    usuarios = carregar_lista_usuarios_para_seguir(config.arquivo_usuarios_seguir)
    if not usuarios:
        print("[i] Nenhum usuário válido encontrado para seguir. Marcando etapa como concluída.")
        marcar_etapa_seguimento_como_concluida(config.config_file_name)
        config.seguindo_usuarios_concluido = True
        return

    print("\n" + "=" * 70)
    print(f" INICIANDO AÇÃO DE SEGUIR CONTAS (VERSÃO WEB) ({len(usuarios)} perfis encontrados)")
    print("=" * 70)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=config.sockpuppet_dir,
            channel="chrome",
            headless=False,
            args=[
                "--start-maximized",  # <-- Abre o navegador maximizado nativamente pelo sistema
                "--disable-blink-features=AutomationControlled",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-features=CalculateNativeWinOcclusion,IsolateOrigins,site-per-process",
                "--no-sandbox"
            ],
            ignore_default_args=["--enable-automation"],
            viewport=None  # <-- Permite que o Playwright use a resolução real da janela do sistema operacional
        )

        page = context.pages[0] if context.pages else await context.new_page()

        # Injeta script para manter foco simulado mesmo se a janela perder o foco no OS
        await page.add_init_script("""
            Object.defineProperty(document, 'visibilityState', {get: () => 'visible'});
            Object.defineProperty(document, 'hidden', {get: () => false});
            window.addEventListener('visibilitychange', e => e.stopImmediatePropagation(), true);
            window.addEventListener('blur', e => e.stopImmediatePropagation(), true);
        """)

        # =====================================================================
        # ETAPA 1: AQUECIMENTO NA PÁGINA PRINCIPAL WEB (10s a 16s)
        # =====================================================================
        print("\n[+] Acessando a página principal web do TikTok para aquecimento inicial...")
        try:
            await page.goto("https://www.tiktok.com/", wait_until="domcontentloaded", timeout=60000)
            tempo_aquecimento = random.uniform(10.0, 16.0)
            
            print(f"  [Aquecimento] Permanecendo na Home por {tempo_aquecimento:.1f}s...")
            
            # Pequeno movimento mecânico de scroll para simular humano assistindo o feed
            await asyncio.sleep(3.0)
            await page.mouse.wheel(0, 400)
            await asyncio.sleep(tempo_aquecimento - 3.0)

            # Checa se abriu CAPTCHA logo na entrada da Home
            if await verificar_captcha_dom(page):
                resolvido = await aguardar_resolucao_humana(page)
                if not resolvido:
                    print("[-] Timeout na resolução do CAPTCHA na Home. Encerrando ciclo.")
                    await context.close()
                    return

        except Exception as e:
            print(f"  [-] Erro ao carregar Home web do TikTok: {e}")

        # =====================================================================
        # ETAPA 2: NAVEGAÇÃO E SEGUIMENTO DOS PERFIS (VERSÃO WEB)
        # =====================================================================
        for idx, username in enumerate(usuarios, start=1):
            url_perfil = f"https://www.tiktok.com/@{username}"
            print(f"\n[{idx}/{len(usuarios)}] Acessando perfil web: @{username}")

            try:
                response = await page.goto(url_perfil, wait_until="domcontentloaded", timeout=60000)
                if response and response.status >= 400:
                    print(f"  [-] Servidor retornou status HTTP {response.status} para @{username}. Pulando...")
                    continue
            except Exception as e:
                print(f"  [-] Falha ao abrir URL de @{username}: {e}")
                continue

            await asyncio.sleep(random.uniform(3.0, 5.0))

            # Checa se surgiu puzzle ao carregar o perfil do usuário
            if await verificar_captcha_dom(page):
                resolvido = await aguardar_resolucao_humana(page)
                if not resolvido:
                    print("[-] CAPTCHA não foi resolvido a tempo. Interrompendo processo de seguir.")
                    break

            try:
                # Movimento de mouse na tela para simular naturalidade
                await page.mouse.move(random.randint(200, 500), random.randint(200, 400))
                await asyncio.sleep(random.uniform(1.0, 2.0))

                # Pequeno scroll inicial ao entrar no perfil para forçar renderização do cabeçalho
                try:
                    await page.mouse.wheel(0, 250)
                    await asyncio.sleep(1.5)
                except Exception:
                    pass

                btn_seguir = None
                seletor_ampliado = 'button[data-e2e="follow-button"], div[data-e2e="follow-button"]'
                
                try:
                    btn_seguir = await page.wait_for_selector(seletor_ampliado, timeout=5000, state="visible")
                except Exception:
                    pass

                # Fallback: Procura botões que contenham estritamente o texto 'Seguir' ou 'Follow'
                if not btn_seguir:
                    botoes = await page.query_selector_all('button, div[role="button"]')
                    for b in botoes:
                        txt = (await b.text_content() or "").strip().lower()
                        if txt in ["seguir", "follow", "seguindo", "following", "mensagem", "message"]:
                            if await b.is_visible():
                                btn_seguir = b
                                break

                if btn_seguir:
                    texto_btn = (await btn_seguir.text_content() or "").strip().lower()
                    print(f"  [DOM] Botão localizado! Texto: '{texto_btn}'")

                    if any(termo in texto_btn for termo in ["seguindo", "following", "mensagem", "message", "amigos", "friends"]):
                        print(f"  [i] Sockpuppet JÁ segue @{username}.")
                    else:
                        await btn_seguir.scroll_into_view_if_needed()
                        await asyncio.sleep(1.0)

                        # Clica utilizando coordenadas reais do mouse baseadas no elemento
                        box = await btn_seguir.bounding_box()
                        if box:
                            x_click = box["x"] + box["width"] / 2 + random.randint(-2, 2)
                            y_click = box["y"] + box["height"] / 2 + random.randint(-2, 2)
                            await page.mouse.move(x_click, y_click)
                            await asyncio.sleep(0.5)
                            await page.mouse.click(x_click, y_click)
                        else:
                            await btn_seguir.click()

                        print(f"  [✓] Ação de 'Seguir' executada com sucesso para @{username}!")

                        await asyncio.sleep(2.5)
                        if await verificar_captcha_dom(page):
                            resolvido = await aguardar_resolucao_humana(page)
                            if not resolvido:
                                break
                else:
                    print(f"  [-] Botão de seguir não retornado/visível/encontrado em @{username}.")

            except Exception as err:
                print(f"  [-] Erro detalhado ao tentar interagir com o botão em @{username}: {err}")

            # =================================================================
            # ETAPA 3: PERMANÊNCIA NO PERFIL (Dwell time de 4s a 10s)
            # =================================================================
            tempo_permanencia = random.uniform(4.0, 10.0)
            print(f"  [Permanência] Visualizando perfil por {tempo_permanencia:.1f}s antes da transição...")
            await page.mouse.wheel(0, random.randint(200, 400))
            await asyncio.sleep(tempo_permanencia)

            # Pausas maiores entre contas (Lotes de 5)
            if idx % 5 == 0 and idx < len(usuarios):
                pausa_lote = random.uniform(20.0, 70.0)
                print(f"  [Pausa de Lote] Resfriando sessão por {pausa_lote:.1f}s a cada 5 perfis...")
                await asyncio.sleep(pausa_lote)
            else:
                tempo_transicao = random.uniform(8.0, 18.0)
                print(f"  [Pausa Stealth] Aguardando {tempo_transicao:.1f}s para o próximo perfil...")
                await asyncio.sleep(tempo_transicao)

        await context.close()

    # Se percorreu a lista, marca a flag como concluída
    config.seguindo_usuarios_concluido = True
    marcar_etapa_seguimento_como_concluida(config.config_file_name)
    print("\n[✓] Etapa de seguir usuários (versão web) finalizada com sucesso!")
