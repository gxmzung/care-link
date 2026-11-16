"""v0.4 demo routes for reproducible synthetic experiment results."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from .benchmark import run

router = APIRouter(prefix="/demo", tags=["demo"])

@router.get("/result")
def result():
    return run()

@router.get("", response_class=HTMLResponse)
def page():
    return """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<title>CARE-LINK | 검증 시연</title>
<style>body{font-family:system-ui;background:#f2f7f3;color:#163c29;margin:0}
header{background:#166b40;color:white;padding:25px 7%}
main{max-width:1100px;margin:30px auto;padding:0 20px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.card{background:white;padding:24px;border-radius:14px;box-shadow:0 4px 16px #153b2710}
small{color:#68796e}h2{margin-top:0}strong.value{font-size:34px;color:#176d40}
table{width:100%;border-collapse:collapse}th,td{padding:9px;text-align:left;border-bottom:1px solid #ddd}
.warn{padding:16px;background:#fff1ce;border-radius:8px;margin:20px 0}
@media(max-width:700px){.grid{grid-template-columns:1fr}}</style></head>
<body><header><h1>CARE-LINK · 운영최적화 실험</h1><p>합성 방문 데이터 기반 일정 배정 비교 | 연구용 MVP v0.4</p></header>
<main><div class="warn">실제 환자·도로 데이터가 아닌 합성 데이터입니다. 의료기관 실증 성과가 아닙니다. 기준 일정에 제약 위반이 있으면 개선률을 표시하지 않습니다.</div>
<div class="grid"><section class="card"><h2>기준 일정 · ID순 배정</h2><div id="baseline"></div></section>
<section class="card"><h2>OR-Tools 일정 최적화</h2><div id="optimized"></div></section></div>
<section class="card" style="margin-top:20px"><h2>비교 해석</h2><p id="interpretation">실험 실행 중…</p>
<p><small>실험 조건: 합성 방문 6건, 의료진 2명, 가상 평면 좌표, 방문 시간창 및 근무시간 제약</small></p></section>
<section class="card" style="margin-top:20px"><h2>의료진별 최적화 일정</h2><div id="routes"></div></section>
</main><script>
const fmt=m=>String(Math.floor(m/60)).padStart(2,'0')+':'+String(m%60).padStart(2,'0');
fetch('/demo/result').then(r=>{if(!r.ok)throw Error('API 실패');return r.json()}).then(d=>{
for(const key of ['baseline','optimized']){const x=d[key];document.getElementById(key).innerHTML=
'<p><strong class="value">'+x.assigned_count+'</strong>건 배정</p>'+
'<p>이동시간: <b>'+x.travel_minutes+'분</b></p>'+
'<p>시간 제약 위반: <b>'+x.constraint_violations+'건</b></p>'+
(key==='optimized'?'<p>미배정: <b>'+x.unassigned.length+'건</b></p>':'');}
const ok=d.comparison_valid;
document.getElementById('interpretation').textContent=ok?
'두 일정 모두 시간 제약을 준수합니다. 동일한 합성 조건에서 이동시간을 비교할 수 있습니다.':
'기준 일정에 시간 제약 위반이 있어 이동시간 감소율을 유효한 성과로 해석할 수 없습니다. 최적화 일정의 배정 및 제약 준수 여부를 확인하세요.';
document.getElementById('routes').innerHTML=d.optimized.routes.map(r=>'<h3>'+r.clinician_id+'</h3><table><tr><th>방문</th><th>도착</th><th>종료</th><th>이동(분)</th></tr>'+r.visits.map(v=>'<tr><td>'+v.id+'</td><td>'+fmt(v.arrival)+'</td><td>'+fmt(v.departure)+'</td><td>'+v.travel+'</td></tr>').join('')+'</table>').join('');
}).catch(e=>document.getElementById('interpretation').textContent='실행 오류: '+e.message);
</script></body></html>"""
