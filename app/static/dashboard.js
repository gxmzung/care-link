(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const refreshButton = $("refresh-button");
  const notice = $("notice");
  let noticeTimer;

  function setNotice(message, kind) {
    window.clearTimeout(noticeTimer);
    notice.textContent = message;
    notice.className = "notice" + (kind ? " " + kind : "");
    notice.hidden = false;
    noticeTimer = window.setTimeout(() => { notice.hidden = true; }, 6000);
  }

  function setLoading(loading, refresh) {
    refreshButton.disabled = loading;
    refreshButton.classList.toggle("loading", loading);
    refreshButton.setAttribute("aria-busy", String(loading));
    refreshButton.querySelector(".refresh-label").textContent = loading
      ? (refresh ? "10개 실험 재계산 중…" : "실험 결과 불러오는 중…")
      : "실험 결과 새로고침";
  }

  async function fetchJSON(url, options) {
    let response;
    try {
      response = await fetch(url, options);
    } catch (error) {
      throw new Error("서버에 연결할 수 없습니다. FastAPI 실행 상태를 확인해 주세요.");
    }
    let data;
    try {
      data = await response.json();
    } catch (error) {
      throw new Error("서버 응답을 JSON으로 해석할 수 없습니다.");
    }
    if (!response.ok) {
      throw new Error(data.detail || "실험 API 요청에 실패했습니다.");
    }
    return data;
  }

  function percent(value, digits) {
    return typeof value === "number" ? value.toFixed(digits) + "%" : "비교 불가";
  }

  function expectedVisitCount(data) {
    return data.scenarios.reduce((total, row) => total + (Number(row.visits) || 0), 0);
  }

  function renderScenarios(data) {
    const total = Number(data.scenario_count) || 0;
    const comparable = Number(data.comparable_scenarios) || 0;
    const assigned = Number(data.optimized_assigned) || 0;
    const expected = expectedVisitCount(data);
    const violations = Number(data.optimized_violations) || 0;

    $("mean-reduction").innerHTML = typeof data.mean_reduction_percent_comparable_only === "number"
      ? data.mean_reduction_percent_comparable_only.toFixed(2) + "<small>%</small>"
      : "<small>비교 불가</small>";
    $("comparable-scenarios").innerHTML = comparable + " <small>/ " + total + "</small>";
    $("optimized-assigned").innerHTML = assigned + " <small>/ " + expected + "</small>";
    $("optimized-violations").innerHTML = violations + "<small> 건</small>";

    const values = data.scenarios
      .map((row) => row.travel_reduction_percent)
      .filter((value) => typeof value === "number");
    const scale = Math.max(1, ...values.map((value) => Math.abs(value)));
    const chart = $("scenario-chart");
    chart.replaceChildren();

    data.scenarios.forEach((row) => {
      const valid = typeof row.travel_reduction_percent === "number";
      const column = document.createElement("div");
      column.className = "bar-column";

      const number = document.createElement("span");
      number.className = "bar-number" + (valid ? "" : " unavailable");
      number.textContent = valid ? row.travel_reduction_percent.toFixed(1) + "%" : "미비교";

      const bar = document.createElement("span");
      const negative = valid && row.travel_reduction_percent < 0;
      bar.className = "bar" + (negative ? " negative" : "") + (valid ? "" : " unavailable");
      bar.style.height = valid ? Math.max(8, Math.abs(row.travel_reduction_percent) / scale * 112) + "px" : "8px";

      const label = document.createElement("span");
      label.className = "bar-label";
      label.textContent = "S" + row.seed;
      column.setAttribute("aria-label", "시드 " + row.seed + ": " + number.textContent);
      column.append(number, bar, label);
      chart.appendChild(column);
    });

    $("minimum-reduction").textContent = percent(data.min_reduction_percent_comparable_only, 2);
    $("median-reduction").textContent = percent(data.median_reduction_percent_comparable_only, 2);
    $("maximum-reduction").textContent = percent(data.max_reduction_percent_comparable_only, 2);

    $("validation-assigned").textContent = assigned + " / " + expected + "건";
    $("validation-violations").textContent = "위반 " + violations + "건";
    updateStatus($("assignment-status"), expected > 0 && assigned === expected);
    updateStatus($("violation-status"), violations === 0);
  }

  function updateStatus(element, passed) {
    element.textContent = passed ? "PASS" : "CHECK";
    element.className = "status " + (passed ? "pass" : "fail");
  }

  function renderSingleComparison(data) {
    const baseline = data.baseline || {};
    const optimized = data.optimized || {};
    const baselineMinutes = Number(baseline.travel_minutes);
    const optimizedMinutes = Number(optimized.travel_minutes);
    const hasMinutes = Number.isFinite(baselineMinutes) && Number.isFinite(optimizedMinutes);
    const maximum = hasMinutes ? Math.max(baselineMinutes, optimizedMinutes, 1) : 1;

    $("baseline-minutes").textContent = Number.isFinite(baselineMinutes) ? baselineMinutes + "분" : "—";
    $("optimized-minutes").textContent = Number.isFinite(optimizedMinutes) ? optimizedMinutes + "분" : "—";
    $("baseline-fill").style.width = Number.isFinite(baselineMinutes) ? baselineMinutes / maximum * 100 + "%" : "0";
    $("optimized-fill").style.width = Number.isFinite(optimizedMinutes) ? optimizedMinutes / maximum * 100 + "%" : "0";

    const delta = $("single-delta");
    delta.replaceChildren();
    const description = document.createElement("span");
    const value = document.createElement("strong");

    if (data.comparison_valid === true && hasMinutes && baselineMinutes > 0) {
      const change = (optimizedMinutes - baselineMinutes) / baselineMinutes * 100;
      description.textContent = "동일 단일 시나리오 이동시간 차이";
      value.textContent = (change < 0 ? "−" : change > 0 ? "+" : "") + Math.abs(change).toFixed(1) + "%";
      delta.className = "delta";
    } else {
      description.textContent = "시간 제약 불충족 · 이동시간 비교 불가";
      value.textContent = "";
      delta.className = "delta invalid";
    }
    delta.append(description, value);
  }

  async function loadDashboard(refresh) {
    setLoading(true, refresh);
    const scenarioRequest = refresh
      ? fetchJSON("/demo/scenarios/refresh", { method: "POST" })
      : fetchJSON("/demo/scenarios");

    const [scenarioResult, singleResult] = await Promise.allSettled([
      scenarioRequest,
      fetchJSON("/demo/result")
    ]);

    const errors = [];
    if (scenarioResult.status === "fulfilled") renderScenarios(scenarioResult.value);
    else errors.push("반복 실험: " + scenarioResult.reason.message);

    if (singleResult.status === "fulfilled") renderSingleComparison(singleResult.value);
    else errors.push("단일 실험: " + singleResult.reason.message);

    if (errors.length) setNotice(errors.join(" "), "");
    else if (refresh) setNotice("10개 반복 실험을 새로 계산해 화면에 반영했습니다.", "success");
    setLoading(false, refresh);
  }

  refreshButton.addEventListener("click", () => loadDashboard(true));
  loadDashboard(false);
})();
