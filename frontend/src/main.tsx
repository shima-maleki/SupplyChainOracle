import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Activity, AlertTriangle, Bot, CloudRain, Database, MapPin, Send, Ship, TrendingUp } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ReactNode } from "react";

import { askAssistant, getDashboard } from "./lib/api";
import { fallbackDashboard } from "./lib/fallbackData";
import type { ChatResponse, DashboardSummary, Region, RiskLevel } from "./types/api";
import "./styles.css";
import { useEffect, useMemo, useState } from "react";

const levelClass: Record<RiskLevel, string> = {
  High: "level level-high",
  Medium: "level level-medium",
  Low: "level level-low"
};

function App() {
  const [dashboard, setDashboard] = useState<DashboardSummary>(fallbackDashboard);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDashboard()
      .then((data) => {
        setDashboard(data);
        setError(null);
      })
      .catch(() => {
        setError("Using local fallback data. Start the FastAPI backend for live API responses.");
      })
      .finally(() => setLoading(false));
  }, []);

  const chartData = useMemo(
    () => dashboard.regions.map((region) => ({ name: region.name, score: region.risk_score })),
    [dashboard.regions]
  );

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Activity size={24} />
          <div>
            <strong>SupplyChainOracle</strong>
            <span>Risk Intelligence</span>
          </div>
        </div>
        <nav>
          <a href="#dashboard">Dashboard</a>
          <a href="#regions">Regions</a>
          <a href="#assistant">Assistant</a>
          <a href="#feed">Feed</a>
        </nav>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <p>Enterprise risk monitoring MVP</p>
            <h1>AI Supply Chain Risk Assistant</h1>
          </div>
          <span className={loading ? "status loading" : "status"}>{loading ? "Loading" : "Operational"}</span>
        </header>

        {error ? <div className="notice">{error}</div> : null}

        <section id="dashboard" className="metric-grid">
          <Metric title="Global Risk Index" value={dashboard.global_risk_index} icon={<TrendingUp />} detail="0 to 100 composite score" />
          <Metric title="High Risk Regions" value={dashboard.high_risk_regions.length} icon={<AlertTriangle />} detail="Regions needing attention" />
          <Metric title="Disruptions Today" value={dashboard.disruptions_today} icon={<Ship />} detail="Weather, news, trade signals" />
          <Metric title="Data Sources" value={4} icon={<Database />} detail="Weather, news, trade, history" />
        </section>

        <section className="dashboard-grid">
          <div className="panel wide">
            <PanelHeader title="Regional Risk Scores" icon={<MapPin />} />
            <div className="chart">
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Bar dataKey="score" fill="#2563eb" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div id="regions" className="panel">
            <PanelHeader title="Europe Risk Map" icon={<CloudRain />} />
            <div className="map-grid">
              {dashboard.regions.map((region) => (
                <RegionTile key={region.id} region={region} />
              ))}
            </div>
          </div>
        </section>

        <section className="dashboard-grid">
          <AssistantPanel />
          <FeedPanel dashboard={dashboard} />
        </section>
      </section>
    </main>
  );
}

function Metric({ title, value, detail, icon }: { title: string; value: number; detail: string; icon: ReactNode }) {
  return (
    <article className="metric">
      <div className="metric-icon">{icon}</div>
      <span>{title}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

function PanelHeader({ title, icon }: { title: string; icon: ReactNode }) {
  return (
    <div className="panel-header">
      <h2>{title}</h2>
      <span>{icon}</span>
    </div>
  );
}

function RegionTile({ region }: { region: Region }) {
  return (
    <article className="region-tile">
      <div>
        <strong>{region.name}</strong>
        <span>{region.risk_score}</span>
      </div>
      <span className={levelClass[region.risk_level]}>{region.risk_level}</span>
    </article>
  );
}

function AssistantPanel() {
  const [question, setQuestion] = useState("What risks are affecting Europe today?");
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [pending, setPending] = useState(false);

  async function submit() {
    setPending(true);
    try {
      const answer = await askAssistant(question);
      setResponse(answer);
    } catch {
      setResponse({
        summary: "The backend is not reachable. Start FastAPI to use the assistant endpoint.",
        risk_level: "Medium",
        key_drivers: ["Local fallback state"],
        affected_regions: ["Europe"],
        citations: []
      });
    } finally {
      setPending(false);
    }
  }

  return (
    <div id="assistant" className="panel">
      <PanelHeader title="AI Assistant" icon={<Bot />} />
      <div className="assistant-box">
        <textarea value={question} onChange={(event) => setQuestion(event.target.value)} />
        <button onClick={submit} disabled={pending}>
          <Send size={16} />
          {pending ? "Analyzing" : "Ask"}
        </button>
      </div>
      {response ? (
        <div className="answer">
          <span className={levelClass[response.risk_level]}>{response.risk_level}</span>
          <p>{response.summary}</p>
          <h3>Key Drivers</h3>
          <ul>
            {response.key_drivers.map((driver) => (
              <li key={driver}>{driver}</li>
            ))}
          </ul>
          {response.citations.length ? (
            <>
              <h3>Sources</h3>
              <ul>
                {response.citations.map((citation) => (
                  <li key={`${citation.source}-${citation.title}`}>
                    {citation.url ? <a href={citation.url}>{citation.title}</a> : citation.title} · {citation.source}
                  </li>
                ))}
              </ul>
            </>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}

function FeedPanel({ dashboard }: { dashboard: DashboardSummary }) {
  return (
    <div id="feed" className="panel">
      <PanelHeader title="Disruption Feed" icon={<Ship />} />
      <div className="feed">
        {dashboard.recent_disruptions.map((item) => (
          <article key={item.id} className="feed-item">
            <span className={levelClass[item.severity]}>{item.severity}</span>
            <div>
              <strong>{item.title}</strong>
              <p>{item.description}</p>
              <small>
                {item.region} · {item.source}
              </small>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
