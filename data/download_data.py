"""
Descarga los datos de partidos internacionales desde GitHub.
Fuente: https://github.com/martj42/international_results
Archivos: results.csv, goalscorers.csv
"""

import os
import sys
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config


# URLs directas al raw CSV en GitHub (branch main)
GITHUB_BASE = "https://raw.githubusercontent.com/martj42/international_results/master"
FILES = {
    "results.csv": f"{GITHUB_BASE}/results.csv",
    "goalscorers.csv": f"{GITHUB_BASE}/goalscorers.csv",
}

# Columnas esperadas para validación
EXPECTED_COLUMNS = {
    "results.csv": ["date", "home_team", "away_team", "home_score", "away_score", "tournament"],
    "goalscorers.csv": ["date", "home_team", "away_team", "team", "scorer"],
}


def download_file(url: str, dest_path: str, force: bool = False) -> bool:
    """
    Descarga un archivo desde una URL y lo guarda en dest_path.
    
    Args:
        url: URL del archivo a descargar
        dest_path: Ruta destino donde guardar el archivo
        force: Si True, sobreescribe archivos existentes
        
    Returns:
        True si la descarga fue exitosa
    """
    if os.path.exists(dest_path) and not force:
        size_mb = os.path.getsize(dest_path) / (1024 * 1024)
        print(f"  ⏭️  {os.path.basename(dest_path)} ya existe ({size_mb:.1f} MB). Usa --force para sobreescribir.")
        return True

    print(f"  ⬇️  Descargando {os.path.basename(dest_path)}...")
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    pct = downloaded / total_size * 100
                    print(f"\r  ⬇️  Descargando... {pct:.0f}%", end="", flush=True)
        
        size_mb = os.path.getsize(dest_path) / (1024 * 1024)
        print(f"\r  ✅ {os.path.basename(dest_path)} descargado ({size_mb:.1f} MB)")
        return True
        
    except requests.RequestException as e:
        print(f"\n  ❌ Error descargando {os.path.basename(dest_path)}: {e}")
        return False


def validate_csv(filepath: str, expected_cols: list[str]) -> bool:
    """
    Valida que un CSV tenga las columnas esperadas.
    
    Args:
        filepath: Ruta al archivo CSV
        expected_cols: Lista de columnas que deben existir
        
    Returns:
        True si la validación pasa
    """
    try:
        import pandas as pd
        df = pd.read_csv(filepath, nrows=5)
        missing = [col for col in expected_cols if col not in df.columns]
        if missing:
            print(f"  ⚠️  Columnas faltantes en {os.path.basename(filepath)}: {missing}")
            return False
        print(f"  ✅ {os.path.basename(filepath)} validado ({len(df.columns)} columnas)")
        return True
    except Exception as e:
        print(f"  ❌ Error validando {os.path.basename(filepath)}: {e}")
        return False


def download_all(force: bool = False) -> bool:
    """
    Descarga todos los archivos de datos necesarios.
    
    Args:
        force: Si True, sobreescribe archivos existentes
        
    Returns:
        True si todas las descargas y validaciones fueron exitosas
    """
    print("\n📦 Descargando datos de partidos internacionales...")
    print(f"   Fuente: github.com/martj42/international_results\n")
    
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    all_ok = True
    for filename, url in FILES.items():
        dest = os.path.join(config.DATA_DIR, filename)
        
        if not download_file(url, dest, force):
            all_ok = False
            continue
        
        # Validar columnas
        if filename in EXPECTED_COLUMNS:
            if not validate_csv(dest, EXPECTED_COLUMNS[filename]):
                all_ok = False
    
    if all_ok:
        print("\n✅ Todos los datos descargados y validados correctamente.")
    else:
        print("\n⚠️  Algunos archivos tuvieron problemas. Revisa los errores arriba.")
    
    return all_ok


if __name__ == "__main__":
    force = "--force" in sys.argv
    download_all(force=force)
