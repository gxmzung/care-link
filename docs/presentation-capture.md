# CARE-LINK v0.6 발표 화면 실행 및 캡처

이 문서는 CARE-LINK 연구용 대시보드를 Windows에서 실행하고 발표자료용 1600×900 화면을 캡처하는 절차를 설명합니다.

## 1. Windows PowerShell에서 실행

저장소 루트에서 다음 명령을 실행합니다.

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

브라우저에서 <http://127.0.0.1:8765/demo>를 엽니다. 최초 접속은 시드 0~9의 OR-Tools 반복 실험을 계산하므로 약 10초 이상 걸릴 수 있습니다. 화면의 `실험 결과 새로고침` 버튼은 캐시를 비우고 10개 실험을 실제로 다시 계산합니다.

OR-Tools DLL 로딩 오류가 발생하면 `docs/windows-winerror-4551.md`를 확인합니다.

## 2. 1600×900 화면 캡처

Chrome 배율을 100%로 맞춥니다. 개발자 도구(`F12`)를 열고 장치 도구 모음(`Ctrl+Shift+M`)에서 다음 값을 지정합니다.

- 반응형(Responsive) 화면 크기: `1600 × 900`
- Device pixel ratio: `1`
- 페이지 확대/축소: `100%`
- 데이터 로딩이 끝나고 새로고침 버튼이 다시 활성화될 때까지 대기

개발자 도구 명령 메뉴(`Ctrl+Shift+P`)에서 `Capture screenshot`을 실행하면 현재 1600×900 뷰포트를 PNG로 저장할 수 있습니다. 주소창까지 포함한 운영체제 캡처가 아니라 웹 페이지 뷰포트 캡처를 사용합니다.

Chrome 헤드리스 캡처가 필요한 경우, 먼저 브라우저에서 페이지를 한 번 열어 반복 실험 캐시를 준비한 뒤 별도 PowerShell 창에서 다음 명령을 실행합니다.

```powershell
& "$env:ProgramFiles\Google\Chrome\Application\chrome.exe" `
  --headless=new `
  --hide-scrollbars `
  --force-device-scale-factor=1 `
  --window-size=1600,900 `
  --virtual-time-budget=20000 `
  --screenshot="$PWD\docs\screenshots\care-link-v0.6-dashboard.png" `
  http://127.0.0.1:8765/demo
```

저장소에 포함된 검증 캡처는 [care-link-v0.6-dashboard.png](screenshots/care-link-v0.6-dashboard.png)입니다.

## 3. 화면 수치의 의미

- `반복 실험 평균 이동시간 감소율`은 시드 0~9의 합성 시나리오에서 **마감시간 우선 독립 탐욕 기준 일정**과 OR-Tools 일정을 비교한 값입니다. 양쪽 일정이 전건 배정되고 시간 제약을 만족한 시나리오만 평균에 포함합니다.
- `단일 일정 비교`는 별도의 방문 6건 합성 시나리오에서 **ID순 기준 일정**과 OR-Tools 일정을 비교합니다. 현재 재현 결과는 120분과 95분이지만, 화면은 `/demo/result` 응답을 동적으로 표시합니다.
- 단일 비교에서 양쪽 일정이 유효하지 않으면 감소율을 숨기고 `시간 제약 불충족 · 이동시간 비교 불가`를 표시합니다.
- `Python 자동 테스트 21 / 21 통과`는 실시간 CI 상태가 아니라 **2026-11-16 로컬 검증 기록**입니다. 반복 실험의 배정 건수와 제약 위반 건수는 현재 API 결과에서 계산합니다.

## 4. PPT 사용 주의사항

- 이 화면은 합성 방문정보와 가상 평면 좌표를 사용한 연구용 실험입니다.
- 반복 실험 10개 표본을 일반화된 통계적 성과로 표현하지 않습니다.
- 43.51% 또는 화면에 표시되는 최신 계산값을 특정 의료기관의 검증된 개선율이나 경제적 절감 효과로 표현하지 않습니다.
- 실제 도로 경로, 환자·주소·진료기록, 의료적 판단, EMR 연계, 현장 도입 성과가 구현 또는 검증됐다고 설명하지 않습니다.
- PPT에 삽입할 때 화면 아래의 합성 데이터 및 현장 미실증 면책 문구를 자르지 않습니다.
