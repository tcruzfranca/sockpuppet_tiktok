from dataclasses import dataclass

@dataclass
class SockpuppetConfig:
    sockpuppet_name: str = ""
    snapshots_dir: str = "./snapshots_"
    sockpuppet_dir: str = "./navegador_dados_"
    session_file: str = "./tiktok_session_"
    orientacao: str = "neutro"  # 'balanceado', 'direita', 'esquerda' ou 'neutro'
    partidos: str = ""          # ex: 'pt', 'pl', 'pt,pl', vazio por padrão para perfis neutros

    # Controle da etapa de seguir perfis
    seguindo_usuarios_concluido: bool = False
    arquivo_usuarios_seguir: str = "usuario_partido_orientacao_tiktok.txt"

    #dados do intervalo de coleta
    quantidade_intervalos_dormindo: int = 1
    intervalos_em_segundos: int = 3600

    config_file_name = "config.toml"


