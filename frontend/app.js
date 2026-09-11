(() => {
  const $ = (id) => document.getElementById(id);

  const state = {
    api: localStorage.getItem("ccr_api") || "",
    sessionId: localStorage.getItem("ccr_session") || "",
    providers: [],
    cursor: 0,
    stream: null,
    graph: { nodes: [], pending_permissions: [] },
    running: false,
    healthTimer: null,
  };

  function apiUrl(path) {
    const base = ($("api-base").value || state.api || "").replace(/\/$/, "");
    return `${base}${path}`;
  }

  async function req(path, opts) {
    const res = await fetch(apiUrl(path), {
      headers: { "Content-Type": "application/json", ...(opts && opts.headers) },
      ...opts,
    });
    const text = await res.text();
    let data = null;
    try { data = text ? JSON.parse(text) : null; } catch { data = { raw: text }; }
    if (!res.ok) {
      const detail = data && (data.detail || data.message);
      throw new Error(detail || `${res.status} ${res.statusText}`);
    }
    return data;
  }

  function setHealth(ok, label) {
    const el = $("health-pill");
    el.textContent = label;
    el.className = `pill ${ok ? "ok" : "bad"}`;
  }

  function renderGate(snap) {
    const line = $("gate-line");
    const ul = $("gate-remaining");
    if (!line || !ul) return;
    if (!snap) {
      line.textContent = "Desktop status unavailable";
      ul.innerHTML = "";
      return;
    }
    const ver = snap.version || "";
    const exit = snap.exit_met ? "exit met" : "exit open";
    line.textContent = `v${ver} · phase ${snap.phase || 4} · ${exit} · path /desktop/windows-path · ci /desktop/ci-trigger · watch /desktop/ci-watch · pull /desktop/ci-pull · install /desktop/ci-install · verify /desktop/ci-verify · go /desktop/ci-go · host /desktop/windows-host · pack /desktop/pack-check · artifacts /desktop/ci-artifacts · drop /desktop/ci-drop · apply /desktop/ci-apply · finish /desktop/ci-finish · live /desktop/ci-live · boot /desktop/ci-boot · seal /desktop/ci-seal · exit /desktop/ci-exit · remain /desktop/remain · block /desktop/host-block · next /desktop/host-next · copy /desktop/host-copy · brief /desktop/host-brief · line /desktop/host-line · now /desktop/host-now · pin /desktop/host-pin · go /desktop/host-go · run /desktop/host-run · watch /desktop/host-watch · pull /desktop/host-pull · hold /desktop/host-hold · wait /desktop/host-wait · stay /desktop/host-stay · keep /desktop/host-keep · sync /desktop/host-sync · lock /desktop/host-lock · echo /desktop/host-echo · mark /desktop/host-mark · stamp /desktop/host-stamp · ack /desktop/host-ack · note /desktop/host-note · flag /desktop/host-flag · seal /desktop/host-seal · sign /desktop/host-sign · ok /desktop/host-ok · fit /desktop/host-fit · cue /desktop/host-cue · tap /desktop/host-tap · aim /desktop/host-aim · fix /desktop/host-fix · set /desktop/host-set · map /desktop/host-map · row /desktop/host-row · key /desktop/host-key · pad /desktop/host-pad · tab /desktop/host-tab · bar /desktop/host-bar · dot /desktop/host-dot · cap /desktop/host-cap · hub /desktop/host-hub · lab /desktop/host-lab · net /desktop/host-net · bus /desktop/host-bus · way /desktop/host-way · yew /desktop/host-yew · ivy /desktop/host-ivy · bay /desktop/host-bay · fig /desktop/host-fig · tea /desktop/host-tea · dew /desktop/host-dew · fog /desktop/host-fog · sun /desktop/host-sun · sky /desktop/host-sky · sea /desktop/host-sea · ice /desktop/host-ice · gem /desktop/host-gem · ore /desktop/host-ore · tin /desktop/host-tin · lead /desktop/host-lead · zinc /desktop/host-zinc · iron /desktop/host-iron · gold /desktop/host-gold · ink /desktop/host-ink · wax /desktop/host-wax · oil /desktop/host-oil · sap /desktop/host-sap · tar /desktop/host-tar · web /desktop/host-web · ray /desktop/host-ray · holt /desktop/host-holt · shaw /desktop/host-shaw · lea /desktop/host-lea · mead /desktop/host-mead · wold /desktop/host-wold · moor /desktop/host-moor · fen /desktop/host-fen`;
    ul.innerHTML = "";
    const items = snap.remaining && snap.remaining.length
      ? snap.remaining
      : [snap.next || "Phase 4 exit met on this host"];
    for (const item of items) {
      const li = document.createElement("li");
      li.textContent = item;
      ul.appendChild(li);
    }
  }

  function setRunStatus(label) {
    $("run-status").textContent = label;
  }

  function renderProviders() {
    const sel = $("provider");
    sel.innerHTML = "";
    for (const p of state.providers) {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = p.label || p.id;
      sel.appendChild(opt);
    }
    fillModels();
  }

  function fillModels() {
    const id = $("provider").value;
    const p = state.providers.find((x) => x.id === id);
    const sel = $("model");
    sel.innerHTML = "";
    const models = (p && ((p.free_models && p.free_models.length) ? p.free_models : p.models)) || [];
    for (const m of models) {
      const opt = document.createElement("option");
      opt.value = m;
      opt.textContent = m;
      sel.appendChild(opt);
    }
    if (p && p.default_model) sel.value = p.default_model;
  }

  function setSessionLine() {
    $("session-line").textContent = state.sessionId
      ? `Active ${state.sessionId.slice(0, 8)}`
      : "No session";
  }

  function renderSessions(items) {
    const ul = $("session-list");
    ul.innerHTML = "";
    for (const s of items.slice(0, 12)) {
      const li = document.createElement("li");
      li.textContent = `${s.provider} · ${(s.model || "?").slice(0, 28)}`;
      li.title = s.session_id;
      li.onclick = () => {
        state.sessionId = s.session_id;
        localStorage.setItem("ccr_session", s.session_id);
        setSessionLine();
        loadEvents();
        loadGraph();
      };
      ul.appendChild(li);
    }
  }

  function renderCatalog(tools, skills) {
    $("tool-count").textContent = String((tools && tools.count) || 0);
    $("skill-count").textContent = String((skills && skills.count) || 0);
    const ul = $("skill-domains");
    ul.innerHTML = "";
    for (const d of (skills && skills.domains) || []) {
      const li = document.createElement("li");
      li.textContent = d;
      ul.appendChild(li);
    }
  }

  function eventKind(ev) {
    return String(ev.type || ev.event_type || ev.kind || "event").toLowerCase();
  }

  function eventText(ev) {
    return ev.message || ev.text || ev.content || ev.summary || JSON.stringify(ev.payload || ev);
  }

  function ingestEvent(ev) {
    const kind = eventKind(ev);
    const stream = $("stream");
    if (stream.classList.contains("empty")) {
      stream.classList.remove("empty");
      stream.textContent = "";
    }
    const row = document.createElement("div");
    row.className = "evt";
    if (kind.includes("think") || kind.includes("reason")) row.classList.add("thinking");
    if (kind.includes("source")) row.classList.add("source");
    if (kind.includes("permission")) row.classList.add("perm");
    if (kind.includes("fail") || kind.includes("error")) row.classList.add("fail");
    row.innerHTML = `<div class="kind">${kind}</div><div>${escapeHtml(String(eventText(ev)).slice(0, 800))}</div>`;
    stream.prepend(row);

    if (kind.includes("source")) {
      const ul = $("sources");
      const li = document.createElement("li");
      li.textContent = String(eventText(ev)).slice(0, 160);
      ul.prepend(li);
    }
    if (kind.includes("permission") || kind.includes("child") || kind.includes("started") || kind.includes("completed")) {
      loadGraph();
    }
    if (typeof ev.index === "number") state.cursor = Math.max(state.cursor, ev.index + 1);
  }

  function statusClass(status) {
    const s = String(status || "").toLowerCase();
    if (s.includes("fail") || s.includes("cancel")) return "status-fail";
    if (s.includes("wait") || s.includes("pending") || s.includes("queued")) return "status-wait";
    if (s.includes("succeed") || s.includes("complet") || s.includes("partial")) return "status-ok";
    return "";
  }

  function drawTree() {
    const el = $("agent-tree");
    const nodes = state.graph.nodes || [];
    el.innerHTML = "";
    if (!nodes.length) {
      el.classList.add("empty");
      el.textContent = "No graph yet";
      return;
    }
    el.classList.remove("empty");
    const byId = new Map(nodes.map((n) => [n.id, n]));
    const children = new Map();
    for (const n of nodes) {
      const parent = n.parent_id && byId.has(n.parent_id) ? n.parent_id : null;
      if (!children.has(parent)) children.set(parent, []);
      children.get(parent).push(n);
    }
    const walk = (id, depth) => {
      const list = children.get(id) || [];
      for (const rec of list) {
        const div = document.createElement("div");
        const live = /run|think|start|verif/i.test(rec.status || "");
        div.className = "agent" + (depth ? " child" : "") + (live ? " active" : "");
        const sc = statusClass(rec.status);
        div.innerHTML = `<div class="name">${escapeHtml(rec.domain || rec.role || "agent")}</div><div class="meta ${sc}">${escapeHtml((rec.role || "worker"))} · ${escapeHtml(rec.status || "")}</div>`;
        el.appendChild(div);
        walk(rec.id, depth + 1);
      }
    };
    walk(null, 0);
    if (!el.childElementCount) {
      for (const rec of nodes) {
        const div = document.createElement("div");
        div.className = "agent";
        div.innerHTML = `<div class="name">${escapeHtml(rec.domain || "agent")}</div><div class="meta">${escapeHtml(rec.status || "")}</div>`;
        el.appendChild(div);
      }
    }
  }

  function drawPerms() {
    const ul = $("perms");
    ul.innerHTML = "";
    const pending = state.graph.pending_permissions || [];
    for (const p of pending) {
      const li = document.createElement("li");
      li.className = "perm-item";
      li.innerHTML = `<div>${escapeHtml(p.tool_name)} · ${escapeHtml(p.risk || "")}</div>`;
      const actions = document.createElement("div");
      actions.className = "actions";
      const yes = document.createElement("button");
      yes.type = "button";
      yes.textContent = "Allow";
      yes.onclick = () => decidePerm(p.request_id, "approved");
      const no = document.createElement("button");
      no.type = "button";
      no.className = "deny";
      no.textContent = "Deny";
      no.onclick = () => decidePerm(p.request_id, "denied");
      actions.appendChild(yes);
      actions.appendChild(no);
      li.appendChild(actions);
      ul.appendChild(li);
    }
  }

  async function decidePerm(requestId, decision) {
    if (!state.sessionId) return;
    try {
      await req(`/session/${state.sessionId}/permissions/${requestId}`, {
        method: "POST",
        body: JSON.stringify({ decision }),
      });
      await loadGraph();
    } catch (err) {
      ingestEvent({ type: "error", message: err.message });
    }
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  async function loadEvents() {
    if (!state.sessionId) return;
    try {
      const data = await req(`/session/${state.sessionId}/events?after=0`);
      $("stream").innerHTML = "";
      $("stream").classList.add("empty");
      for (const ev of data.events || []) ingestEvent(ev);
    } catch {
      /* session may be stale */
    }
  }

  async function loadGraph() {
    if (!state.sessionId) return;
    try {
      state.graph = await req(`/session/${state.sessionId}/graph`);
      drawTree();
      drawPerms();
    } catch {
      /* ignore */
    }
  }

  function openStream() {
    if (state.stream) state.stream.close();
    if (!state.sessionId) return;
    const url = apiUrl(`/events/${state.sessionId}?after=${state.cursor}`);
    const es = new EventSource(url);
    state.stream = es;
    es.onmessage = (msg) => {
      try { ingestEvent(JSON.parse(msg.data)); } catch { /* keep-alive */ }
    };
  }

  async function boot() {
    $("api-base").value = state.api;
    $("api-base").addEventListener("change", () => {
      state.api = $("api-base").value.trim();
      localStorage.setItem("ccr_api", state.api);
      refresh();
    });
    $("provider").addEventListener("change", fillModels);
    $("btn-refresh").addEventListener("click", refresh);
    $("btn-session").addEventListener("click", createSession);
    $("btn-run").addEventListener("click", runTask);
    $("btn-settings").addEventListener("click", () => openSettings(false));
    $("btn-settings-close").addEventListener("click", closeSettings);
    $("btn-settings-skip").addEventListener("click", skipFirstRun);
    $("settings-form").addEventListener("submit", (ev) => {
      ev.preventDefault();
      saveSettings();
    });
    await refresh();
    await maybeFirstRun();
    if (state.sessionId) {
      setSessionLine();
      await loadEvents();
      await loadGraph();
    }
  }

  function openSettings(firstRun) {
    $("settings-title").textContent = firstRun ? "First run" : "Settings";
    $("settings-lead").textContent = firstRun
      ? "Save provider keys and local tool endpoints. Values stay in .agentforge/settings.json."
      : "Update keys, PinchTab, and Agent-Reach. Blank secret fields keep the stored value.";
    $("settings-msg").textContent = "";
    $("settings-layer").classList.remove("hidden");
  }

  function closeSettings() {
    $("settings-layer").classList.add("hidden");
  }

  function fillSettingsForm(s) {
    $("set-gemini").value = "";
    $("set-opencode").value = "";
    $("set-openai").value = "";
    $("set-groq").value = "";
    $("set-github").value = "";
    $("set-pinchtab-token").value = "";
    $("set-reach-token").value = "";
    $("set-ollama").value = s.ollama_base_url || "";
    $("set-pinchtab-url").value = s.pinchtab_url || "";
    $("set-reach-url").value = s.agent_reach_base_url || "";
    $("set-workspace").value = s.workspace || $("workspace").value || "";
    if (s.workspace && !$("workspace").value) $("workspace").value = s.workspace;
  }

  async function maybeFirstRun() {
    try {
      const data = await req("/settings");
      const s = data.settings || {};
      fillSettingsForm(s);
      if (!s.first_run_done) openSettings(true);
    } catch {
      /* settings route may be down */
    }
  }

  async function skipFirstRun() {
    try {
      await req("/settings", {
        method: "PUT",
        body: JSON.stringify({ first_run_done: true }),
      });
    } catch {
      /* local skip still closes */
    }
    closeSettings();
  }

  async function saveSettings() {
    const payload = {
      first_run_done: true,
      ollama_base_url: $("set-ollama").value.trim(),
      pinchtab_url: $("set-pinchtab-url").value.trim(),
      agent_reach_base_url: $("set-reach-url").value.trim(),
      workspace: $("set-workspace").value.trim(),
    };
    const secrets = {
      gemini_api_key: $("set-gemini").value.trim(),
      opencode_api_key: $("set-opencode").value.trim(),
      openai_api_key: $("set-openai").value.trim(),
      groq_api_key: $("set-groq").value.trim(),
      github_token: $("set-github").value.trim(),
      pinchtab_token: $("set-pinchtab-token").value.trim(),
      agent_reach_token: $("set-reach-token").value.trim(),
    };
    for (const [k, v] of Object.entries(secrets)) {
      if (v) payload[k] = v;
    }
    try {
      await req("/settings", { method: "PUT", body: JSON.stringify(payload) });
      if (payload.workspace) $("workspace").value = payload.workspace;
      $("settings-msg").textContent = "Saved";
      closeSettings();
    } catch (err) {
      $("settings-msg").textContent = err.message;
    }
  }

  function showEngineWait(on, detail) {
    const layer = $("engine-layer");
    if (!layer) return;
    if (on) layer.classList.remove("hidden");
    else layer.classList.add("hidden");
    if (detail && $("engine-msg")) $("engine-msg").textContent = detail;
  }

  function watchHealth() {
    if (state.healthTimer) return;
    state.healthTimer = setInterval(() => {
      refresh();
    }, 2000);
  }

  function stopWatchHealth() {
    if (!state.healthTimer) return;
    clearInterval(state.healthTimer);
    state.healthTimer = null;
  }

  async function refresh() {
    try {
      const health = await req("/health");
      const ver = health.version ? ` ${health.version}` : "";
      setHealth(true, `AgentForge${ver}`);
      showEngineWait(false);
      stopWatchHealth();
    } catch (err) {
      setHealth(false, "engine down");
      showEngineWait(true, err.message + " — retrying. Use Doctor-AgentForge.bat if this persists.");
      watchHealth();
      return;
    }
    const [providers, sessions, tools, skills, gate] = await Promise.all([
      req("/providers"),
      req("/session"),
      req("/tools"),
      req("/skills"),
      req("/desktop/status").catch(() => null),
    ]);
    state.providers = providers.providers || [];
    renderProviders();
    renderSessions(sessions.sessions || []);
    renderCatalog(tools, skills);
    renderGate(gate);
    if (state.sessionId) await loadGraph();
  }

  async function createSession() {
    const body = {
      provider: $("provider").value,
      model: $("model").value || null,
      api_key: $("api-key").value || null,
      workspace: $("workspace").value || null,
      permission_mode: $("perm-mode").value,
    };
    const session = await req("/session", { method: "POST", body: JSON.stringify(body) });
    state.sessionId = session.session_id;
    state.cursor = 0;
    state.graph = { nodes: [], pending_permissions: [] };
    localStorage.setItem("ccr_session", state.sessionId);
    setSessionLine();
    drawTree();
    drawPerms();
    $("stream").innerHTML = "";
    $("stream").classList.add("empty");
    $("stream").textContent = "Events appear here";
    await refresh();
    openStream();
  }

  async function runTask() {
    if (!state.sessionId) await createSession();
    const objective = $("objective").value.trim();
    if (!objective) return;
    $("btn-run").disabled = true;
    state.running = true;
    setRunStatus("Running");
    openStream();
    const poll = setInterval(loadGraph, 1200);
    try {
      const result = await req("/run", {
        method: "POST",
        body: JSON.stringify({
          session_id: state.sessionId,
          objective,
          plan_only: $("plan-only").checked,
        }),
      });
      const status = (result && result.status) || "completed";
      setRunStatus(status);
      ingestEvent({ type: "completed", message: result.message || "run finished", payload: result.detail });
    } catch (err) {
      setRunStatus("Failed");
      ingestEvent({ type: "error", message: err.message });
    } finally {
      clearInterval(poll);
      state.running = false;
      $("btn-run").disabled = false;
      await loadGraph();
    }
  }

  boot();
})();
