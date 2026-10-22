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
import json
import os
import time
import random
from typing import Optional
from datetime import datetime
from playwright.async_api import async_playwright
from SockpuppetConfig import SockpuppetConfig


# ==============================================================================
# CONFIGURAÇÕES DO SOCK PUPPET
# ==============================================================================
config: Optional[SockpuppetConfig] = None

# ==============================================================================
# CONFIGURAÇÕES E CACHE EM MEMÓRIA DOS PARTIDOS
# ==============================================================================
# Estruturas globais para cache em memória das 50 primeiras contas
CACHE_PARTIDOS = {}        # { uniqueId: "PT" ou "PL" }
CONTAS_VALIDAS_PT = set()  # Primeiras 50 contas válidas do PT
CONTAS_VALIDAS_PL = set()  # Primeiras 50 contas válidas do PL

def setup_sockpuppet_standalone_vars():

    global config #SOCK_PUPPET_NAME, SNAPSHOTS_DIR, SOCK_PUPPET_DIR
    config = SockpuppetConfig()

    print("Inicie com letras e use apenas letras e números.")
    config.sockpuppet_name = input("Nomeie do sockpuppet-audit: ")
    config.sockpuppet_dir += config.sockpuppet_name
    config.snapshots_dir += config.sockpuppet_name


def setup_sockpuppet_vars(configParam: SockpuppetConfig):

    global config
    config = configParam


def get_output_filename(base_path_identifier):
    """Gera o nome do arquivo dinâmico com sockpuppet e timestamp atual (YYYYMMDD_HHMMSS)."""
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_path_identifier}_tiktok_snapshot_{timestamp_str}.json"


def carregar_base_partidos(caminho_arquivo: str = "usuario_partido_orientacao_tiktok.txt"):
    """Lê o arquivo de mapeamento e guarda em memória apenas as 50 primeiras contas do PT e PL."""
    global CACHE_PARTIDOS, CONTAS_VALIDAS_PT, CONTAS_VALIDAS_PL
    
    if not os.path.exists(caminho_arquivo):
        print(f"[-] Arquivo de mapeamento não encontrado: {caminho_arquivo}")
        return

    contador_pt, contador_pl = 0, 0

    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        for linha in f:
            partes = linha.strip().split(";")
            if len(partes) >= 2:
                user = partes[0].strip().lower().replace("@", "")
                partido = partes[1].strip().upper()
                
                CACHE_PARTIDOS[user] = partido
                
                if partido == "PT" and contador_pt < 50:
                    CONTAS_VALIDAS_PT.add(user)
                    contador_pt += 1
                elif partido == "PL" and contador_pl < 50:
                    CONTAS_VALIDAS_PL.add(user)
                    contador_pl += 1

    print(f"[+] Base carregada em memória: {len(CONTAS_VALIDAS_PT)} contas PT e {len(CONTAS_VALIDAS_PL)} contas PL (restritas às 50 primeiras).")



async def executar_curtida_humanizada(page) -> bool:
    """
    Simula o comportamento humano de consumo (dwell time, espera orgânica,
    movimento natural do ponteiro) antes de acionar a curtida no player do TikTok.
    """
    print("\n[+] [Ação] Iniciando simulação de consumo humanizado (Dwell Time para Curtida)...")
    try:
        await page.mouse.wheel(0, random.randint(200, 350))
        
        tempo_consumo = random.uniform(5.0, 9.0)
        print(f"  [Humano] Assistindo ao vídeo por {tempo_consumo:.1f}s antes de interagir...")
        await asyncio.sleep(tempo_consumo)

        viewport = page.viewport_size or {"width": 1920, "height": 1080}
        centro_x = (viewport["width"] / 2) + random.randint(-30, 30)
        centro_y = (viewport["height"] / 2) + random.randint(-30, 30)

        print(f"  [Humano] Movendo o mouse suavemente para ({centro_x:.1f}, {centro_y:.1f})...")
        await page.mouse.move(centro_x, centro_y, steps=random.randint(15, 25))
        await asyncio.sleep(random.uniform(0.5, 1.2))

        await page.mouse.click(centro_x, centro_y)
        await asyncio.sleep(0.8)

        print("  [Teclado] Pressionando o atalho de curtida ('L')...")
        await page.keyboard.press("l")
        await asyncio.sleep(2.5)

        print("  [✓] Ciclo de curtida humanizada concluído com sucesso!")
        return True

    except Exception as err:
        print(f"  [-] Erro no fluxo de curtida humanizada: {err}")
    
    return False

#método usado apenas para teste.
async def testar_curtida_segundo_item(page) -> bool:
    """
    Simula o comportamento humano de consumo (dwell time, espera orgânica,
    movimento natural do ponteiro) antes de acionar a curtida no player do TikTok.
    """
    print("\n[+] [Passo 1] Iniciando simulação de consumo humanizado (Dwell Time)...")
    try:
        # 1. Pequeno scroll natural para fixar o vídeo na tela
        await page.mouse.wheel(0, random.randint(200, 350))
        
        # 2. DWELL TIME: Simula o tempo que um humano gasta assistindo ao vídeo (entre 5 e 9 segundos)
        tempo_consumo = random.uniform(5.0, 9.0)
        print(f"  [Humano] Assistindo ao vídeo por {tempo_consumo:.1f}s antes de interagir...")
        await asyncio.sleep(tempo_consumo)

        # 3. MOVER O MOUSE ORGANICAMENTE: Move o cursor de forma suave em direção ao centro do player
        viewport = page.viewport_size or {"width": 1920, "height": 1080}
        centro_x = (viewport["width"] / 2) + random.randint(-30, 30)
        centro_y = (viewport["height"] / 2) + random.randint(-30, 30)

        print(f"  [Humano] Movendo o mouse suavemente para ({centro_x:.1f}, {centro_y:.1f})...")
        await page.mouse.move(centro_x, centro_y, steps=random.randint(15, 25))
        await asyncio.sleep(random.uniform(0.5, 1.2))

        # 4. Clique de foco na área ativa do player
        await page.mouse.click(centro_x, centro_y)
        await asyncio.sleep(0.8)

        # 5. Dispara a tecla 'L' (atalho nativo de like do TikTok Web) com atraso realista
        print("  [Teclado] Pressionando o atalho de curtida ('L')...")
        await page.keyboard.press("l")
        
        # Pausa pós-curtida para registrar o estado visual na interface
        await asyncio.sleep(2.5)

        print("  [✓] [Passo 1] Ciclo de curtida humanizada concluído com sucesso!")
        return True

    except Exception as err:
        print(f"  [-] Erro no fluxo de curtida humanizada: {err}")
    
    return False

async def main():
    # Carrega a base de partidos em memória no início de cada execução
    carregar_base_partidos("usuario_partido_orientacao_tiktok.txt")

    captured_items = {}  # Dicionário mapeado por id do item
    api_counter = 0      # Contador de posição na ordem da API

    async def handle_response(response):
        nonlocal api_counter
        url = response.url
        # Captura as requisições XHR/Fetch de feed do TikTok
        if "tiktok.com" in url and response.status == 200:
            if any(k in url for k in ["item_list", "recommend", "detail"]):
                try:
                    data = await response.json()
                    items_list = data.get("itemList") or data.get("items") or []
                    for item in items_list:
                        video_id = item.get("id") or item.get("idStr")
                        if video_id and video_id not in captured_items:
                            api_counter += 1
                            
                            # =========================================================================
                            # EXTRAÇÃO DE DADOS E MAPEAMENTO DOS CAMPOS DA API DO TIKTOK
                            # =========================================================================

                            # Informações do Autor (Perfil)
                            author_info = item.get("author", {})
                            unique_id = author_info.get("uniqueId") or author_info.get("unique_id", "anon")
                            unique_id_lower = unique_id.lower()
                            author_id = author_info.get("id") or author_info.get("author_id")
                            verified = author_info.get("verified") or author_info.get("is_verified", False)
                            is_followed = (
                                author_info.get("isFollowed", False) or 
                                author_info.get("followStatus") == 1
                            )

                            # Identifica o partido do autor consultando o cache em memória
                            partido_autor = CACHE_PARTIDOS.get(unique_id_lower, "DESCONHECIDO")
                            
                            # Classificação do Tipo de Mídia
                            if "imagePost" in item or item.get("mediaType") == 2:
                                media_type = "image_carousel"
                            elif item.get("mediaType") == 1 or "video" in item:
                                media_type = "video"
                            else:
                                media_type = "text_or_other"

                            relative_path = (
                                f"/@{unique_id}/video/{video_id}" 
                                if media_type == "video" 
                                else f"/@{unique_id}/photo/{video_id}"
                            )

                            # Flags de Anúncio, Conteúdo Pago e Restrições de Plataforma
                            is_ad = item.get("isAd", False) or "adAuthorization" in item
                            is_paid_content = (
                                item.get("isPaidContent", False) or 
                                item.get("promotedItem", False) or 
                                item.get("itemPaidType", 0) > 0
                            )
                            contents_warnings = item.get("contents") or item.get("warnings") or []

                            # Rotulagem de Inteligência Artificial e Motivo da Recomendação
                            aigc_label = item.get("aigcLabelType") or item.get("isAIGCGenerated")
                            is_aigc_generated = bool(aigc_label and aigc_label != 0)

                            item_recommend_reason = (
                                item.get("itemRecommendReason") or 
                                item.get("recommendReason", {}).get("text") or 
                                None
                            )

                            # Conversão da Data de Criação do Post
                            create_time_unix = item.get("createTime") or item.get("create_time")
                            create_time_iso = (
                                datetime.fromtimestamp(int(create_time_unix)).isoformat()
                                if create_time_unix else None
                            )

                            # Estatísticas e Métricas de Engajamento do Post
                            stats = item.get("stats", {}) or item.get("statistics", {})

                            # =========================================================================
                            # MONTAGEM DO DICIONÁRIO FINAL COM DOCUMENTAÇÃO EXPLICATIVA DOS CAMPOS
                            # =========================================================================
                            captured_items[video_id] = {
                                # Identificador único numérico da publicação no TikTok (padrão de 19 dígitos).
                                "id": video_id,

                                # Tipo de mídia do post ('video', 'image_carousel' ou 'text_or_other').
                                "mediaType": media_type,

                                # URI relativa compacta para o post no navegador (ex: /@username/video/12345).
                                "relative_path": relative_path,

                                # Texto completo da legenda / descrição escrita pelo autor na publicação.
                                "desc": item.get("desc", ""),

                                # Timestamp ISO 8601 correspondente ao momento exato em que o post foi publicado.
                                "createTime": create_time_iso,

                                # Carimbo de data/hora (ISO) de quando o robô raspou esta publicação.
                                "captured_at": datetime.now().isoformat(),

                                # Posição sequencial absoluta em que a publicação chegou no lote da API (ordem da rede).
                                "api_arrival_index": api_counter,

                                # Posição sequencial em que o elemento foi efetivamente renderizado na tela (DOM).
                                "visual_feed_index": None,

                                # Objeto com dados do perfil do criador do conteúdo
                                "author": {
                                    # Handle público do perfil do autor (o nome com '@').
                                    "uniqueId": unique_id,

                                    # ID numérico interno e exclusivo do usuário no banco do TikTok.
                                    "id": author_id,

                                    # Booleano (true/false) indicando se o perfil possui selo azul de verificação.
                                    "verified": verified,

                                    # Booleano (true/false) indicando se a conta coletora (sockpuppet) já segue o autor.
                                    "isFollowed": is_followed
                                },

                                # Booleano (true/false) que indica se o post é um anúncio pago via TikTok Ads.
                                "isAd": is_ad,

                                # Booleano (true/false) que indica se é post promocional, monetizado ou parceria paga.
                                "isPaidContent": is_paid_content,

                                # Booleano (true/false) indicando se a publicação contém rótulo oficial de criação por IA (AIGC).
                                "isAIGCGenerated": is_aigc_generated,

                                # Texto descritivo que explica por que o algoritmo recomendou este post no seu feed.
                                "itemRecommendReason": item_recommend_reason,

                                # Lista de avisos/restrições da plataforma (ex: avisos de sensibilidade, idade ou risco).
                                "contents": contents_warnings,

                                # Dicionário de estatísticas e métricas de engajamento no momento exato da captura
                                "stats": {
                                    # Número total de visualizações (play count) acumuladas até a captura.
                                    "playCount": stats.get("playCount") or stats.get("play_count"),

                                    # Número total de curtidas/likes (digg count) recebidas.
                                    "diggCount": stats.get("diggCount") or stats.get("digg_count"),

                                    # Número total de comentários publicados na postagem.
                                    "commentCount": stats.get("commentCount") or stats.get("comment_count"),

                                    # Número total de vezes que o post foi compartilhado.
                                    "shareCount": stats.get("shareCount") or stats.get("share_count"),

                                    # Número total de vezes que o post foi salvo/adicionado aos favoritos.
                                    "collectCount": stats.get("collectCount") or stats.get("collect_count")
                                }
                            }
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] API Batch #{api_counter} [{media_type}]: @{unique_id} (ID: {video_id})")
                except Exception:
                    pass

    async with async_playwright() as p:
        print("Iniciando o Chrome com o perfil logado...")
        
        # Flags para desativar a suspensão do renderizador do Ubuntu/Chrome
        context = await p.chromium.launch_persistent_context(
            user_data_dir= config.sockpuppet_dir,
            channel="chrome",
            headless=False,
            args=[
                "--start-maximized",  # <-- Abre o navegador maximizado nativamente pelo sistema
                "--disable-blink-features=AutomationControlled", # Mascara a flag navigator.webdriver
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--no-sandbox"
            ],
            ignore_default_args=["--enable-automation"],  # Remove a infobar do Chrome de automação
            viewport=None  # <-- Permite que o Playwright use a resolução real da janela do sistema operacional
        )

        page = context.pages[0] if context.pages else await context.new_page()
        page.on("response", lambda res: asyncio.create_task(handle_response(res)))

        print("Forçando navegação por JS (sem aguardar o socket do Playwright)...")
        await page.evaluate("window.location.href = 'https://www.tiktok.com/foryou'")

        espera_carregar_pag = random.randint(8,14)
        print("Aguardando 10 segundos para carregar a página...")
        await asyncio.sleep(espera_carregar_pag)

        # =========================================================================
        # PAUSA PARA TESTE COMPORTAMENTAL / HIPÓTESE HUMANA
        # =========================================================================
        #print("\n" + "=" * 70)
        #print(" [PAUSA DE TESTE DE RESIDÊNCIA/MUSEU DE DADOS]")
        #print(" O navegador está aberto no feed do TikTok.")
        #print(" Faça os testes manuais na janela do Chrome (mexa o mouse, permaneça no feed).")
        #print(" Quando quiser que o robô continue o teste de curtida e coleta:")
        #print(" --> Volte neste terminal e PRESSIONA ENTER.")
        #print("=" * 70 + "\n")
        
        # O script congela aqui até você apertar ENTER no terminal
        #input(">>> Pressione [ENTER] para liberar a execução do robô...")
        #exit()

        # =========================================================================
        # =========================================================================
        # TESTE DO PASSO 1: Curtir o 2º item visível do feed
        # =========================================================================
        #await testar_curtida_segundo_item(page)
        # =========================================================================

        print("Iniciando rolagem mecânica na página e captura do feed visual...")
        visual_counter = 0


        print("Iniciando rolagem mecânica na página e captura do feed visual...")
        visual_counter = 0
        seen_visual_ids = set()

        for i in range(1, 12):
            print(f"Tentativa de rolagem {i}/11...")

            # 1. Tira do React / DOM o ID do vídeo atualmente ativo na tela do usuário
            active_video_id = await page.evaluate("""
                () => {
                    // Estratégia A: Busca pelo ID do post na URL do navegador se houver alteração dinâmica de History
                    const urlMatch = window.location.href.match(/(?:video|photo)\\/(\\d{18,20})/);
                    if (urlMatch) return urlMatch[1];

                    // Estratégia B: Inspeciona as instâncias do Player/Container visíveis no centro da tela (Viewport)
                    const elements = Array.from(document.querySelectorAll('div[data-e2e*="feed-item"], article, div[class*="ItemContainer"]'));
                    const windowHeight = window.innerHeight;

                    for (const el of elements) {
                        const rect = el.getBoundingClientRect();
                        // Checa se o elemento ocupa o centro vertical da tela
                        if (rect.top <= windowHeight / 2 && rect.bottom >= windowHeight / 2) {
                            // Procura qualquer atributo data-* ou link interno
                            const html = el.innerHTML + " " + Array.from(el.attributes).map(a => a.value).join(' ');
                            const match = html.match(/(?:video|photo)\\/(\\d{18,20})/) || html.match(/\\b(\\d{18,20})\\b/);
                            if (match) return match[1];
                        }
                    }

                    // Estratégia C: Fallback para o elemento <video> com estado de reprodução
                    const videos = Array.from(document.querySelectorAll('video'));
                    for (const v of videos) {
                        let parent = v.parentElement;
                        for (let depth = 0; depth < 8 && parent; depth++) {
                            const match = parent.innerHTML.match(/(?:video|photo)\\/(\\d{18,20})/) || parent.outerHTML.match(/\\b(\\d{18,20})\\b/);
                            if (match) return match[1];
                            parent = parent.parentElement;
                        }
                    }

                    return null;
                }
            """)

            # 2. Se a inspeção do DOM não encontrar o ID específico, preenche o visual_feed_index
            # com base na Fila Sequencial do Feed da API (já que a web carrega exatamente na ordem da API)
            if active_video_id and active_video_id in captured_items and active_video_id not in seen_visual_ids:
                visual_counter += 1
                seen_visual_ids.add(active_video_id)
                captured_items[active_video_id]["visual_feed_index"] = visual_counter
                print(f"  [Visual Feed #{visual_counter}] Post ID associado via DOM: {active_video_id}")
            else:
                # FALLBACK DE SINCRO: Associa o próximo item não atribuído da API
                # No TikTok Web, a ordem visual de scroll é estritamente equivalente à ordem de entrega do XHR
                unassigned_items = [v_id for v_id in captured_items if captured_items[v_id]["visual_feed_index"] is None]
                if unassigned_items:
                    next_id = unassigned_items[0]
                    visual_counter += 1
                    seen_visual_ids.add(next_id)
                    captured_items[next_id]["visual_feed_index"] = visual_counter
                    print(f"  [Visual Feed #{visual_counter}] Post ID associado (Fila API): {next_id}")

            await page.keyboard.press("PageDown")
            await asyncio.sleep(3.5)

        # =========================================================================
        # AVALIAÇÃO DAS REGRAS POLÍTICAS E EXECUÇÃO DE CURTIDAS
        # =========================================================================
        posts_coletados = list(captured_items.values())
        
        # Filtra considerando apenas as 50 primeiras contas válidas do PT e PL
        candidatos_pt = [p for p in posts_coletados if p["partido"] == "PT" and p["author"].lower() in CONTAS_VALIDAS_PT]
        candidatos_pl = [p for p in posts_coletados if p["partido"] == "PL" and p["author"].lower() in CONTAS_VALIDAS_PL]

        orientacao = getattr(config, "orientacao", "neutro").lower()
        partido_alvo = getattr(config, "partido_alvo", "").upper()
        nome_sockpuppet = getattr(config, "sockpuppet_name", "padrao")

        posts_curtidos_neste_ciclo = []

        print(f"\n[+] Aplicando regras para perfil [Orientação: {orientacao} | Partido Alvo: {partido_alvo}]")

        if orientacao in ["esquerda", "direita"] and partido_alvo in ["PT", "PL"]:
            alvo_lista = candidatos_pt if partido_alvo == "PT" else candidatos_pl
            # Tenta curtir até 2 publicações disponíveis conforme regra
            curtidas_feitas = 0
            for post_alvo in alvo_lista:
                if curtidas_feitas < 2:
                    print(f"[+] Encontrado post elegível do {partido_alvo} (@{post_alvo['author']}). Curtindo...")
                    if await executar_curtida_humanizada(page):
                        posts_curtidos_neste_ciclo.append(post_alvo)
                        curtidas_feitas += 1
                        await asyncio.sleep(3.0)

        elif orientacao == "balanceado":
            print("[+] Perfil BALANCEADO: Verificando simetria (1 PT e 1 PL)...")
            if candidatos_pt and candidatos_pl:
                print("[✓] Critério atendido! Curtindo 1 post do PT e 1 do PL...")
                # Curte 1 do PT
                if await executar_curtida_humanizada(page):
                    posts_curtidos_neste_ciclo.append(candidatos_pt[0])
                await asyncio.sleep(3.0)
                # Curte 1 do PL
                if await executar_curtida_humanizada(page):
                    posts_curtidos_neste_ciclo.append(candidatos_pl[0])
            else:
                print("[-] Critério balanceado não atingido neste ciclo (faltou PT ou PL). Nenhuma curtida realizada.")

        elif orientacao == "neutro":
            print("[*] Perfil NEUTRO: Nenhuma curtida programada.")

        # =========================================================================
        # GERAÇÃO DO SNAPSHOT DE DADOS E DO LOG DE CURTIDAS
        # =========================================================================
        if posts_coletados:
            os.makedirs(config.snapshots_dir, exist_ok=True)
            base_identifier = os.path.join(config.snapshots_dir, config.sockpuppet_name)
            output_filename = get_output_filename(base_identifier)
            output_filepath = os.path.abspath(output_filename)

            with open(output_filepath, "w", encoding="utf-8") as f:
                json.dump(posts_coletados, f, ensure_ascii=False, indent=4)
            print(f"\n[✓] SNAPSHOT GERADO: {output_filepath} ({len(posts_coletados)} itens)")
        
        # Cria a pasta 'curtidas-[nome-sockpuppet]' nos moldes do snapshot
        pasta_curtidas = f"curtidas-{nome_sockpuppet}"
        os.makedirs(pasta_curtidas, exist_ok=True)

        timestamp_str = datetime.now().strftime("%Y%m%d-%H%M%S")
        arquivo_log = os.path.join(pasta_curtidas, f"curtida-{nome_sockpuppet}-{timestamp_str}.txt")

        # Salva as publicações curtidas ou mantém o arquivo em branco se não houver posts curtidos
        with open(arquivo_log, "w", encoding="utf-8") as f_log:
            if posts_curtidos_neste_ciclo:
                f_log.write(f"RELATÓRIO DE CURTIDAS - CICLO {timestamp_str}\n")
                f_log.write(f"Sockpuppet: {nome_sockpuppet} | Orientação: {orientacao}\n")
                f_log.write("=" * 60 + "\n\n")
                for p in posts_curtidos_neste_ciclo:
                    f_log.write(f"ID do Vídeo: {p['id']}\n")
                    f_log.write(f"Autor: @{p['author']} (Partido: {p['partido']})\n")
                    f_log.write(f"Descrição: {p['desc']}\n")
                    f_log.write(f"Curtidas Totais (diggCount): {p['stats'].get('diggCount', 0)}\n")
                    f_log.write("-" * 40 + "\n")
            else:
                # Arquivo fica em branco se não existia publicação disponível para curtir no ciclo
                pass

        print(f"[✓] LOG DE CURTIDAS GRAVADO: {arquivo_log}")
        await context.close()
            
        '''
        result_list = list(captured_items.values())

        if result_list:
            # Garante que a pasta informada em SNAPSHOTS_DIR existe no sistema antes de abrir o arquivo
            os.makedirs(config.snapshots_dir, exist_ok=True)

            # Prepara o caminho concatenado de forma segura
            base_identifier = os.path.join(config.snapshots_dir, config.sockpuppet_name)

            output_filename = get_output_filename(base_identifier)
            output_filepath = os.path.abspath(output_filename)

            # Salvando no arquivo
            with open(output_filepath, "w", encoding="utf-8") as f:
                json.dump(result_list, f, ensure_ascii=False, indent=4)
            print(f"\n ARQUIVO GERADO: {output_filepath} ({len(result_list)} itens)")
        else:
            print("\n Se a tela continuou em branco, faça UM CLIQUE manual dentro da janela do Chrome assim que ela abrir para dar foco do Ubuntu a ela.")

        await context.close()
        '''

async def setup_sockpuppet_in_loop():
    print("Iniciando configuração do sockpuppet para coleta das impreesions (feeds) na timeline.")

    intervalos_em_segundos = config.quantidade_intervalos_dormindo * config.intervalos_em_segundos

    while True:
        print("\n------------------------------------------------")
        print(f" Iniciando novo ciclo de coleta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("--------------------------------------------------")
        
        try:
            await main()
        except Exception as e:
            print(f"Erro durante a execução do script: {e}")

        print(f"\nColeta finalizada. Aguardando {intervalos_em_segundos} segundo(s) para a próxima rodada...")
        # Pausa a execução
        time.sleep(intervalos_em_segundos)

if __name__ == "__main__":

    print("Você está executando o sockTimeline.py de forma isolada. Dê preferência a rodar o pipeline.")
    print("Para isso, para isso, interrompa este script e acesse sockpuppetRun.py.")
    interromper = input("Interromper (S) ou Não (n)?")

    if (interromper == "n"):
        setup_sockpuppet_standalone_vars()
        asyncio.run(setup_sockpuppet_in_loop())
    else:
        print("Finalizando sem rodar o script!")



'''
Sobre o código atual e os diferentes tipos de postagens do tiktok.
Publicações de Texto Puro ("mediaType": "text_or_other")
Captura na API: 100% capturado. Se o TikTok entregar uma publicação baseada apenas em texto ou um formato híbrido sem video ou imagePost, o script captura todos os metadados (legenda desc, autor, engajamento, etc.) e classifica como "text_or_other".

Ressalva no DOM: No TikTok para web, publicações puramente de texto muitas vezes são renderizadas usando a estrutura de URL de foto (/photo/ID) ou vídeo (/video/ID). Caso o TikTok renderize um post de texto sem uma tag <a> padrão contendo /video/ ou /photo/, o item continuará salvo no seu JSON com todos os dados da API, mas seu visual_feed_index poderá ficar como null
'''
