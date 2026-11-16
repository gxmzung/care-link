# CARE-LINK — 방문의료 일정·동선 운영지원 MVP

민들레의료복지사회적협동조합 사례 연구를 위한 **독립 연구용 시제품**입니다. 기관의 공식 시스템이 아니며 현장 도입·효과 검증이 완료된 제품이 아닙니다.

## v0.1 구현
- 합성 방문 데이터 6건, 방문 가능 시간 제약
- 단일 의료진 방문 순서 생성(최근접 실행 가능 방문 탐욕 휴리스틱)
- 방문별 도착·종료 시각, 이동시간, 미배정 건 표시
- FastAPI 대시보드 및 `GET /api/sample`, `POST /api/plan`
- pytest 기반 제약 조건 및 API 테스트 5개

## 설치 및 실행
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
http://127.0.0.1:8000 에 접속합니다.

## 테스트
```bash
pytest -q
```

## 제한 사항
좌표와 이동시간은 가상의 평면 좌표·거리 환산에 근거합니다. **실제 도로 기반 경로, 복수 의료진 배정, OR-Tools, AI/LLM, 기준 일정 비교는 미구현**입니다. 최적해를 보장하지 않습니다.

실제 환자정보·주소·진료기록을 입력하지 마세요. 의료 판단 기능이 없습니다. 수치와 화면은 민들레의 실측 성과가 아닙니다.

## 다음 단계
1. 복수 의료진 및 OR-Tools VRPTW
2. 동일 조건의 기준 일정 대비 비교
3. 재현 가능한 모의 실험·테스트 결과 정리
