from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from .optimizer import Visit, schedule, sample_visits

from .v2_api import router as v2_router

app = FastAPI(title="CARE-LINK MVP", version="0.2.0")
app.include_router(v2_router)

class VisitInput(BaseModel):
    id: str = Field(min_length=1, max_length=32)
    x: float = Field(ge=0, le=100)
    y: float = Field(ge=0, le=100)
    earliest: int = Field(ge=0, le=1440)
    latest: int = Field(ge=0, le=1440)
    duration: int = Field(default=30, ge=1, le=480)

class PlanInput(BaseModel):
    visits: list[VisitInput] = Field(min_length=1, max_length=100)
    start_minute: int = Field(default=540, ge=0, le=1440)
    end_minute: int = Field(default=1080, ge=0, le=1440)

@app.get("/api/sample")
def sample():
    visits = sample_visits()
    return {"data_type": "synthetic", "visits": [vars(v) for v in visits], "plan": schedule(visits)}

@app.post("/api/plan")
def plan(data: PlanInput):
    if data.start_minute >= data.end_minute:
        raise HTTPException(422, "start_minute must precede end_minute")
    if len({v.id for v in data.visits}) != len(data.visits):
        raise HTTPException(422, "visit IDs must be unique")
    if any(v.earliest >= v.latest for v in data.visits):
        raise HTTPException(422, "invalid visit time window")
    visits = [Visit(**v.model_dump()) for v in data.visits]
    return {"data_type": "synthetic_or_user_supplied", "plan": schedule(visits, start_minute=data.start_minute, end_minute=data.end_minute)}

@app.get("/", response_class=HTMLResponse)
def home():
    return """<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CARE-LINK MVP</title>
<style>
body{font-family:system-ui,sans-serif;background:#f3f7f4;color:#153b27;margin:0}
header{background:#147343;color:white;padding:22px max(5%,20px)}
main{max-width:1000px;margin:30px auto;padding:0 20px}
.notice{background:#fff3d7;padding:14px;border-radius:8px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:700px){.grid{grid-template-columns:1fr}}
section{background:white;border-radius:12px;padding:20px;box-shadow:0 3px 16px #153b2710}
button{background:#147343;color:white;border:0;border-radius:8px;padding:12px 20px;cursor:pointer}
table{border-collapse:collapse;width:100%}
td,th{padding:10px;border-bottom:1px solid #e1eae4;text-align:left}
small{color:#61776a}.metric{font-size:30px;font-weight:700;color:#147343}
</style></head>
<body><header><h1>CARE-LINK</h1><div>방문의료 일정·동선 운영지원 — 연구용 MVP</div></header>
<main><p class="notice">⚠ 모든 방문 데이터는 가상의 합성 데이터입니다. 실제 환자·주소·진료정보를 입력하지 마세요. 이 버전은 최적해 보장 없이 탐욕적 휴리스틱으로 일정을 생성합니다.</p>
<div class="grid"><section><h2>시뮬레이션 조건</h2><p>방문 대상 <strong id="visits">—</strong>건 · 의료진 <strong>1명</strong></p>
<p>운영시간 09:00–18:00 · 방문당 기본 30분</p>
<button onclick="load()">합성 데이터 일정 계산</button></section>
<section><h2>계산 결과</h2><div class="metric" id="assigned">—</div><small>배정 방문 건수</small>
<p>총 이동시간: <strong id="travel">—</strong>분</p><p>미배정: <strong id="unassigned">—</strong></p></section></div>
<section style="margin-top:18px"><h2>방문 순서 및 시간표</h2>
<table><thead><tr><th>순서</th><th>방문 ID</th><th>도착</th><th>종료</th><th>이동(분)</th></tr></thead><tbody id="rows"></tbody></table></section>
<p><small>실제 도로 경로가 아닌 가상 평면 좌표 기반 이동시간입니다. 의료적 판단·응급 우선순위 결정 기능은 없습니다.</small></p>
</main><script>
const fmt=m=>String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0');
async function load(){try{
let r=await fetch('/api/sample');if(!r.ok)throw Error('API error');
let d=await r.json(),p=d.plan;
document.getElementById('visits').textContent=d.visits.length;
document.getElementById('assigned').textContent=p.assigned_count+'건';
document.getElementById('travel').textContent=p.travel_minutes;
document.getElementById('unassigned').textContent=p.unassigned.join(', ')||'없음';
document.getElementById('rows').innerHTML=p.route.map((v,i)=>'<tr><td>'+(i+1)+'</td><td>'+v.id+'</td><td>'+fmt(v.arrival)+'</td><td>'+fmt(v.departure)+'</td><td>'+v.travel+'</td></tr>').join('');
}catch(e){alert(e.message)}}
load();
</script></body></html>"""
