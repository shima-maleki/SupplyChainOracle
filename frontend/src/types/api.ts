export type RiskLevel = "Low" | "Medium" | "High";

export type Region = {
  id: string;
  name: string;
  risk_score: number;
  risk_level: RiskLevel;
  last_updated: string;
};

export type Disruption = {
  id: string;
  title: string;
  description: string;
  region: string;
  severity: RiskLevel;
  source: string;
  url?: string | null;
  created_at: string;
};

export type TradeMetric = {
  id: string;
  country: string;
  partner_country: string;
  trade_flow: string;
  commodity: string;
  period: string;
  trade_value: number;
  quantity?: number | null;
  created_at: string;
};

export type HistoricalShipment = {
  id: string;
  order_id: string;
  region: string;
  warehouse: string;
  delivery_status: string;
  delay_days: number;
  shipping_mode: string;
  created_at: string;
};

export type DashboardSummary = {
  global_risk_index: number;
  high_risk_regions: Region[];
  disruptions_today: number;
  regions: Region[];
  recent_disruptions: Disruption[];
  trade_metrics: TradeMetric[];
  historical_shipments: HistoricalShipment[];
};

export type SystemStatus = {
  services: Record<"supabase" | "qdrant" | "openai" | "newsapi" | "openweather" | "un_comtrade", boolean>;
  models: {
    chat: string;
    embedding: string;
  };
  rag: {
    collection: string;
    documents: number;
    indexed: boolean;
  };
  data: {
    disruptions: number;
    trade_metrics: number;
  };
};

export type ChatResponse = {
  summary: string;
  risk_level: RiskLevel;
  key_drivers: string[];
  affected_regions: string[];
  citations: Array<{
    title: string;
    source: string;
    url?: string | null;
  }>;
};
