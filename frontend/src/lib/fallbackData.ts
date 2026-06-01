import type { DashboardSummary } from "../types/api";

export const fallbackDashboard: DashboardSummary = {
  global_risk_index: 55,
  high_risk_regions: [
    {
      id: "germany",
      name: "Germany",
      risk_score: 78,
      risk_level: "High",
      last_updated: new Date().toISOString()
    }
  ],
  disruptions_today: 4,
  regions: [
    {
      id: "germany",
      name: "Germany",
      risk_score: 78,
      risk_level: "High",
      last_updated: new Date().toISOString()
    },
    {
      id: "china",
      name: "China",
      risk_score: 60,
      risk_level: "Medium",
      last_updated: new Date().toISOString()
    },
    {
      id: "netherlands",
      name: "Netherlands",
      risk_score: 56,
      risk_level: "Medium",
      last_updated: new Date().toISOString()
    },
    {
      id: "spain",
      name: "Spain",
      risk_score: 24,
      risk_level: "Low",
      last_updated: new Date().toISOString()
    }
  ],
  recent_disruptions: [
    {
      id: "weather-de-storm",
      title: "Heavy storms detected near southern Germany",
      description: "Severe wind and rain risk for freight routes.",
      region: "Germany",
      severity: "High",
      source: "OpenWeather API",
      created_at: new Date().toISOString()
    },
    {
      id: "news-rotterdam-congestion",
      title: "Port congestion reported around Rotterdam",
      description: "Container delays may affect North Sea routes.",
      region: "Netherlands",
      severity: "Medium",
      source: "NewsAPI",
      created_at: new Date().toISOString()
    }
  ],
  trade_metrics: [
    {
      id: "trade-de-imports",
      country: "Germany",
      partner_country: "China",
      trade_flow: "Import",
      commodity: "Industrial components",
      period: "2026-05",
      trade_value: 1240000000,
      quantity: 380000,
      created_at: new Date().toISOString()
    }
  ],
  historical_shipments: [
    {
      id: "hist-1",
      order_id: "ORD-1001",
      region: "Germany",
      warehouse: "Berlin DC",
      delivery_status: "Delayed",
      delay_days: 3,
      shipping_mode: "Road",
      created_at: new Date().toISOString()
    }
  ]
};
