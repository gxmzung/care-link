# CARE-LINK — 방문의료 일정·동선 운영지원 연구용 시제품

CARE-LINK는 합성 방문 데이터를 사용해 복수 의료진의 방문 일정과 이동시간을 비교하는 독립 연구용 시제품입니다. 실제 의료기관의 공식 시스템이 아니며 현장 도입·의료적 효과·경제적 절감 효과가 검증된 제품이 아닙니다.

## v0.6 주요 기능

- FastAPI 기반 발표용 연구 대시보드: `GET /demo`
- ID순 기준 일정과 OR-Tools VRPTW 단일 비교: `GET /demo/result`
- 시드 0~9 반복 합성 실험과 프로세스 캐시: `GET /demo/scenarios`
- 반복 실험 실제 재계산: `POST /demo/scenarios/refresh`
- 기존 `GET /api/sample`, `POST /api/plan`, `POST /api/v2/optimize` 유지
- 비교 가능한 시나리오만 이동시간 감소율 집계
- 합성 데이터, 가상 좌표, 현장 미실증 범위를 화면에 명시

## 설치 및 실행

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

<http://127.0.0.1:8000/demo>에서 대시보드를 확인합니다. 발표용 Windows 실행·캡처 절차는 [docs/presentation-capture.md](docs/presentation-capture.md)를 참고합니다.

## 테스트

```bash
python -m pytest -q
python -m app.benchmark
python -m app.scenario_benchmark
```

## 제한 사항

좌표와 이동시간은 가상의 평면 좌표·거리 환산에 근거합니다. 실제 도로 경로, 환자정보, 주소, 진료기록, 의료적 판단, EMR 연계 기능은 없습니다. 합성 실험 수치를 실제 의료기관의 성과로 해석하지 마세요.
