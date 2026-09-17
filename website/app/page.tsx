"use client";

import { useMemo, useState } from "react";

const projects = [
  { id: "research", num: "01", short: "Research Agent", title: "Autonomous Financial Research", desc: "Evidence-first equity research across filings, fundamentals, macro, news, and quantitative signals.", color: "#ff6846", status: "Runnable outline", icon: "⌁", tags: ["LangGraph", "SEC EDGAR", "Polars"], metric: "0.55", metricLabel: "demo confidence" },
  { id: "forecast", num: "02", short: "Prediction Markets", title: "Prediction Market Intelligence", desc: "Multi-agent probabilistic forecasts tested against live market consensus and proper scoring rules.", color: "#8357ff", status: "Vertical slice", icon: "◎", tags: ["Bayesian", "Calibration", "Polymarket"], metric: "4", metricLabel: "forecast agents" },
  { id: "portfolio", num: "03", short: "Portfolio Engine", title: "AI Portfolio Decision Engine", desc: "Point-in-time allocation research with constrained optimization, event scenarios, and walk-forward backtests.", color: "#00a980", status: "Baseline ready", icon: "◒", tags: ["Optimization", "Risk", "Backtesting"], metric: "6", metricLabel: "allocation methods" },
  { id: "market", num: "04", short: "Market Simulator", title: "Agent-Based Market Simulator", desc: "A deterministic continuous double auction for studying price discovery and heterogeneous agent behavior.", color: "#e5ab00", status: "Research kernel", icon: "⇄", tags: ["Order Book", "Agents", "Gymnasium"], metric: "1 bp", metricLabel: "tick precision" },
  { id: "copilot", num: "05", short: "Research Copilot", title: "Quantitative Research Copilot", desc: "A reproducible path from literature review and hypothesis formation to experiments and critical review.", color: "#2786ff", status: "MVP workflow", icon: "✦", tags: ["Literature", "Experiments", "MLflow"], metric: "10", metricLabel: "research roles" },
];

const activity = [
  ["Research Agent", "AMD evidence report completed", "2m"],
  ["Market Simulator", "Information shock · seed 42", "18m"],
  ["Portfolio Engine", "Walk-forward baseline evaluated", "1h"],
];

export default function Home() {
  const [selected, setSelected] = useState("research");
  const [query, setQuery] = useState("");
  const active = projects.find((p) => p.id === selected) ?? projects[0];
  const filtered = useMemo(() => projects.filter((p) => `${p.title} ${p.tags.join(" ")}`.toLowerCase().includes(query.toLowerCase())), [query]);

  return (
    <main>
      <header className="topbar">
        <a className="brand" href="#top"><span className="brandmark">AQ</span><span>AI Quant Lab</span><i>Research OS</i></a>
        <nav aria-label="Primary"><a href="#projects">Projects</a><a href="#activity">Activity</a><a href="#about">Methodology</a></nav>
        <a className="repoButton" href="https://github.com" target="_blank" rel="noreferrer"><span>↗</span> Repository</a>
      </header>

      <section className="hero" id="top">
        <div className="heroCopy">
          <div className="eyebrow"><span></span> Open research infrastructure</div>
          <h1>Quant systems,<br/><em>made inspectable.</em></h1>
          <p>Five rigorous AI and market research systems. Built for reproducibility, honest evaluation, and questions that deserve more than a black box.</p>
          <div className="heroActions"><a className="primary" href="#projects">Explore the lab <b>↓</b></a><a className="textLink" href="#about">Read our principles <span>→</span></a></div>
        </div>
        <div className="signalPanel" aria-label="Research signal visualization">
          <div className="panelTop"><span>LIVE SYSTEM MAP</span><span className="live"><i></i> 5 projects online</span></div>
          <div className="orbital">
            <div className="orbit orbit1"></div><div className="orbit orbit2"></div>
            <div className="core"><strong>AQ</strong><small>LAB</small></div>
            {projects.map((p, i) => <button key={p.id} onClick={() => {setSelected(p.id); document.getElementById("workspace")?.scrollIntoView({behavior:"smooth"});}} className={`node n${i+1}`} style={{"--node": p.color} as React.CSSProperties} aria-label={`Open ${p.title}`}><span>{p.icon}</span><small>{p.num}</small></button>)}
          </div>
          <div className="panelFoot"><span>REPRODUCIBLE BY DESIGN</span><span>LAST SYNC · NOW</span></div>
        </div>
      </section>

      <section className="ticker" aria-label="Lab principles"><div><span>01</span> POINT-IN-TIME DATA</div><div><span>02</span> DETERMINISTIC BASELINES</div><div><span>03</span> EVIDENCE FIRST</div><div><span>04</span> NO TRADING CLAIMS</div></section>

      <section className="projects" id="projects">
        <div className="sectionHead"><div><span className="kicker">THE LAB</span><h2>Five systems. One research stack.</h2></div><label className="search"><span>⌕</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Filter projects" aria-label="Filter projects"/></label></div>
        <div className="projectGrid">
          {filtered.map((p) => <article className={`projectCard ${selected === p.id ? "selected" : ""}`} key={p.id} onClick={() => setSelected(p.id)} style={{"--accent": p.color} as React.CSSProperties}>
            <div className="cardTop"><span className="projectNum">PROJECT {p.num}</span><span className="status"><i></i>{p.status}</span></div>
            <div className="projectIcon">{p.icon}</div><h3>{p.title}</h3><p>{p.desc}</p>
            <div className="tags">{p.tags.map(t => <span key={t}>{t}</span>)}</div>
            <button onClick={() => {setSelected(p.id); document.getElementById("workspace")?.scrollIntoView({behavior:"smooth"});}}>Open workspace <span>↗</span></button>
          </article>)}
        </div>
      </section>

      <section className="workspace" id="workspace" style={{"--accent": active.color} as React.CSSProperties}>
        <div className="workspaceNav">
          <span className="kicker">ACTIVE WORKSPACE</span>
          <div className="projectTabs">{projects.map(p => <button key={p.id} className={p.id === selected ? "active" : ""} onClick={() => setSelected(p.id)}>{p.num}</button>)}</div>
        </div>
        <div className="workspaceGrid">
          <div className="workspaceCopy"><div className="bigIcon">{active.icon}</div><p className="overline">PROJECT {active.num} / {active.status}</p><h2>{active.title}</h2><p>{active.desc}</p><div className="metric"><strong>{active.metric}</strong><span>{active.metricLabel}</span></div><button className="launch" onClick={() => alert(`${active.title} is documented and ready to run from its project folder.`)}>View project guide <span>→</span></button></div>
          <div className="terminal">
            <div className="terminalTop"><span><i></i><i></i><i></i></span><b>research_run.log</b><small>DEMO</small></div>
            <div className="terminalBody"><p><span>10:42:01</span> Initializing {active.short.toLowerCase()}...</p><p><span>10:42:02</span> Loading point-in-time research contracts</p><p><span>10:42:02</span> <b>✓</b> Validation passed</p><p><span>10:42:03</span> Running deterministic baseline</p><div className="progress"><i></i></div><p><span>10:42:05</span> <b>✓</b> Artifacts recorded with provenance</p><div className="terminalResult"><small>RUN STATUS</small><strong>REPRODUCIBLE</strong><span>seed · 42 &nbsp; / &nbsp; data · demo</span></div></div>
          </div>
        </div>
      </section>

      <section className="bottomGrid">
        <div className="activity" id="activity"><div className="miniHead"><span className="kicker">RECENT ACTIVITY</span><button>View all →</button></div>{activity.map((a,i)=><div className="activityRow" key={a[1]}><span className={`pulse p${i}`}></span><div><strong>{a[0]}</strong><p>{a[1]}</p></div><time>{a[2]} ago</time></div>)}</div>
        <div className="principle" id="about"><span className="kicker">RESEARCH PRINCIPLE / 01</span><blockquote>“If a result cannot be reproduced, inspected, and challenged—it is not a result yet.”</blockquote><p>Every project keeps assumptions visible, prevents look-ahead bias, and separates observed evidence from AI interpretation.</p></div>
      </section>

      <footer><a className="brand" href="#top"><span className="brandmark">AQ</span><span>AI Quant Lab</span></a><p>Research infrastructure for curious, skeptical minds.</p><span>© 2026 · Research & education only</span></footer>
    </main>
  );
}
