import os
import hashlib
import json
from pathlib import Path

# Diretórios e extensões que devem ser ignorados para manter a auditoria limpa
PASTAS_IGNORADAS = {".venv","venv", "__pycache__", ".git", "snapshots_", "navegador_dados_", "curtidas-"}
EXTENSOES_IGNORADAS = {".pyc", ".json", ".sha256"}

def calcular_sha256(caminho_arquivo):
    sha256_hash = hashlib.sha256()
    with open(caminho_arquivo, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def gerar_hashes_projeto(diretorio_raiz="."):
    hashes_dict = {}
    
    for raiz, dirs, arquivos in os.walk(diretorio_raiz):
        # Modifica 'dirs' in-place para evitar entrar em pastas ignoradas
        dirs[:] = [d for d in dirs if d not in PASTAS_IGNORADAS and not d.startswith("curtidas-")]
        
        for arquivo in arquivos:
            caminho_completo = Path(raiz) / arquivo
            
            # Ignora arquivos gerados automaticamente ou extensões indesejadas
            if caminho_completo.suffix in EXTENSOES_IGNORADAS or arquivo == "projeto_hashes.json":
                continue
                
            # Caminho relativo para ficar limpo no JSON
            caminho_relativo = str(caminho_completo.relative_to(diretorio_raiz))
            
            try:
                hash_val = calcular_sha256(caminho_completo)
                hashes_dict[caminho_relativo] = hash_val
                print(f"[OK] {caminho_relativo} -> {hash_val[:12]}...")
            except Exception as e:
                print(f"[-] Erro ao ler {caminho_relativo}: {e}")

    # Salva no arquivo JSON solicitado
    output_filename = "projeto_hashes.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(hashes_dict, f, ensure_ascii=False, indent=4)
        
    print(f"\n[✓] Sucesso! Todos os hashes foram salvos em '{output_filename}'.")

if __name__ == "__main__":
    gerar_hashes_projeto()
