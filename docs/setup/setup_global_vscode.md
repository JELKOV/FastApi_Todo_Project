# 🌍 VS Code 글로벌 설정 가이드

## 방법 1: 사용자 설정 (모든 프로젝트에 적용)

### Windows
```
%APPDATA%\Code\User\settings.json
```

### Linux
```
~/.config/Code/User/settings.json
```

### Mac
```
~/Library/Application Support/Code/User/settings.json
```

### 권장 글로벌 설정
```json
{
    "python.defaultInterpreterPath": "./.venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "python.terminal.activateEnvInCurrentTerminal": true,
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".coverage": true,
        "htmlcov": true
    }
}
```

## 방법 2: 워크스페이스 설정 (현재 방식)

각 프로젝트의 `.vscode/settings.json`에서 프로젝트별 설정
- ✅ 프로젝트별 독립적 설정
- ✅ 팀원들과 설정 공유 가능
- ✅ 프로젝트별 다른 Python 버전 사용 가능

## 권장사항

**워크스페이스 설정을 권장**합니다:
- 프로젝트별로 다른 Python 버전 사용 가능
- 팀원들과 설정 공유 용이
- 프로젝트별 독립적인 개발 환경
