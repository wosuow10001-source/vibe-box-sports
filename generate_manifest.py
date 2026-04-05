import json
import os
import base64
from pathlib import Path

def generate_manifest():
    root_dir = Path(".")
    manifest = {}
    
    # 필수 디렉토리 및 파일 목록
    include_patterns = [
        "app.py",
        "config.py",
        "data.json",
        "sports_data.db",
        "modules/**/*.py",
        "data/**/*.py",
        "data/**/*.db",
        "assets/**/*.*",
        "predict-system/**/*.*",
    ]
    
    # 제외 패턴
    exclude_dirs = {".git", ".venv", "venv", "__pycache__", ".claude", ".vscode", ".kiro"}
    
    print("Generating stlite-manifest.json...")
    
    for pattern in include_patterns:
        for file_path in root_dir.glob(pattern):
            if file_path.is_dir():
                continue
                
            # 제외 디렉토리 체크
            if any(part in exclude_dirs for part in file_path.parts):
                continue
                
            relative_path = str(file_path.relative_to(root_dir)).replace("\\", "/")
            
            try:
                # 텍스트 파일과 이진 파일 구분
                is_binary = file_path.suffix.lower() in {".db", ".png", ".jpg", ".jpeg", ".ico", ".pdf", ".zip"}
                
                if is_binary:
                    with open(file_path, "rb") as f:
                        content = base64.b64encode(f.read()).decode("utf-8")
                        manifest[relative_path] = {
                            "content": content,
                            "encoding": "base64"
                        }
                else:
                    with open(file_path, "r", encoding="utf-8") as f:
                        manifest[relative_path] = f.read()
                
                print(f"  [OK] {relative_path}")
            except Exception as e:
                print(f"  [ERROR] {relative_path}: {e}")
                
    with open("stlite-manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        
    print(f"\nManifest generated successfully with {len(manifest)} files.")

if __name__ == "__main__":
    generate_manifest()
