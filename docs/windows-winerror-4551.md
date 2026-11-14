# Windows WinError 4551 진단

## 증상
`OSError: [WinError 4551] 애플리케이션 제어 정책에서 이 파일을 차단했습니다`

이는 Python 패키지 설치 실패가 아니라 Windows의 애플리케이션 제어 정책이 OR-Tools 네이티브 DLL 로드를 차단한 상황입니다.

## 대응
1. Windows 보안 정책을 임의로 끄거나 DLL을 교체하지 않습니다.
2. 조직 관리 PC라면 관리자에게 OR-Tools 패키지의 허용 여부를 확인합니다.
3. 별도 허용된 Linux 개발환경(예: WSL Ubuntu)에서 동일 저장소를 실행할 수 있습니다. 조직 정책이 WSL 사용도 제한한다면 사용하지 않습니다.
4. GitHub Actions(Linux)에서 테스트 결과와 benchmark.json 아티팩트를 확인할 수 있습니다.

## Windows에서 가능한 최소 확인
```powershell
python -m pytest tests/test_optimizer.py -q
python -m uvicorn app.main:app --reload
```
기본 v0.1 API는 OR-Tools와 무관합니다. v0.2 최적화 API와 /demo/result는 OR-Tools DLL 로드가 차단되면 503 오류를 반환합니다.

## WSL에서 실행 (허용된 환경에서만)
```bash
git clone https://github.com/gxmzung/care-link.git
cd care-link
git switch --track origin/fix/windows-ortools-dll-v0.4.1
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python -m app.benchmark
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Windows 브라우저에서 `http://localhost:8000/demo`에 접속합니다.

**주의:** 위 Linux 실행 명령은 해당 환경에 Python 3.12와 venv가 준비되어 있다는 전제입니다. 사용자 환경에서 직접 검증된 결과는 아닙니다.
