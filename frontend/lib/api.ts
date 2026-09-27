/**
 * BusiAI Frontend API Client
 * Connects to FastAPI backend at http://localhost:8000/api/v1
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface ColumnMetadata {
  name: string;
  original_name: string;
  data_type: string;
  sample_values: any[];
}

export interface DatasetInfo {
  id: string;
  name: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  row_count: number;
  column_count: number;
  columns: ColumnMetadata[];
  table_name: string;
  uploaded_at: string;
  preview_rows: Record<string, any>[];
}

export interface NumericStats {
  min?: number;
  max?: number;
  mean?: number;
  median?: number;
  std?: number;
  q25?: number;
  q75?: number;
  outlier_count: number;
  zero_count: number;
}

export interface CategoricalStats {
  unique_count: number;
  cardinality_ratio: number;
  top_values: { value: string; count: number }[];
}

export interface TemporalStats {
  min_date?: string;
  max_date?: string;
}

export interface ColumnProfile {
  name: string;
  original_name: string;
  inferred_type: string;
  data_type: string;
  total_count: number;
  null_count: number;
  null_percentage: number;
  is_primary_key_candidate: boolean;
  numeric_stats?: NumericStats;
  categorical_stats?: CategoricalStats;
  temporal_stats?: TemporalStats;
}

export interface DatasetProfile {
  dataset_id: string;
  total_rows: number;
  total_columns: number;
  quality_score: number;
  columns: ColumnProfile[];
  primary_date_column?: string;
  key_metrics: string[];
  key_dimensions: string[];
  issues_detected: string[];
}

export interface BusinessInsight {
  id: string;
  type: string;
  importance: "high" | "medium" | "low";
  title: string;
  description: string;
  metric?: string;
  dimension?: string;
  evidence_summary: Record<string, any>;
  suggested_question?: string;
}

export interface CalculationProof {
  metric: string;
  formula: string;
  inputs: Record<string, any>;
  calculated_value: any;
  confidence_pct: number;
}

export interface EvidenceItem {
  id: string;
  title: string;
  hypothesis_id?: string;
  sql_query: string;
  executed_at: string;
  execution_time_ms: number;
  data_points: Record<string, any>[];
  proof: CalculationProof;
  summary: string;
}

export interface Hypothesis {
  id: string;
  statement: string;
  rationale: string;
  target_metric: string;
  target_dimension?: string;
  status: "pending" | "confirmed" | "refuted" | "inconclusive";
  confidence_score: number;
  impact_magnitude?: number;
  evidence_ids: string[];
  explanation?: string;
}

export interface RecommendationAction {
  id: string;
  title: string;
  description: string;
  projected_impact: string;
  priority: "high" | "medium" | "low";
  supporting_evidence: string[];
}

export interface InvestigationResult {
  id: string;
  dataset_id: string;
  question: string;
  target_metric: string;
  executive_summary: string;
  key_findings: string[];
  hypotheses_tested: Hypothesis[];
  evidence_package: EvidenceItem[];
  primary_drivers: Record<string, any>[];
  recommendations: RecommendationAction[];
}

export interface DecisionGraphNode {
  id: string;
  type: string;
  data: Record<string, any>;
  position: { x: number; y: number };
}

export interface DecisionGraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  animated: boolean;
}

export interface DecisionGraphResponse {
  nodes: DecisionGraphNode[];
  edges: DecisionGraphEdge[];
  summary: string;
}

export interface SimulationScenario {
  name: string;
  projected_value: number;
  delta_value: number;
  delta_percentage: number;
  description: string;
}

export interface TimelinePoint {
  month: string;
  baseline: number;
  projected_base: number;
  projected_conservative: number;
  projected_optimistic: number;
}

export interface SimulationResult {
  dataset_id: string;
  target_metric: string;
  baseline_value: number;
  projected_value: number;
  net_delta: number;
  net_delta_pct: number;
  confidence_score: number;
  scenarios: SimulationScenario[];
  timeline_curve: TimelinePoint[];
  key_takeaways: string[];
}

export interface SQLQueryResult {
  success: boolean;
  columns: string[];
  rows: Record<string, any>[];
  row_count: number;
  execution_time_ms: number;
  error?: string;
}

// API Functions

export async function listDatasets(): Promise<DatasetInfo[]> {
  const res = await fetch(`${API_BASE_URL}/datasets`);
  if (!res.ok) throw new Error("Failed to fetch datasets");
  return res.json();
}

export async function uploadDataset(file: File, name?: string): Promise<DatasetInfo> {
  const formData = new FormData();
  formData.append("file", file);
  if (name) formData.append("name", name);

  const res = await fetch(`${API_BASE_URL}/datasets/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Failed to upload dataset");
  }
  const data = await res.json();
  return data.dataset;
}

export async function uploadSampleCsv(filename: string, content: string, name: string): Promise<DatasetInfo> {
  const blob = new Blob([content], { type: "text/csv" });
  const file = new File([blob], filename, { type: "text/csv" });
  return uploadDataset(file, name);
}

export async function getDatasetProfile(datasetId: string): Promise<DatasetProfile> {
  const res = await fetch(`${API_BASE_URL}/profile/${datasetId}`);
  if (!res.ok) throw new Error("Failed to fetch dataset profile");
  return res.json();
}

export async function getDatasetInsights(datasetId: string): Promise<BusinessInsight[]> {
  const res = await fetch(`${API_BASE_URL}/insights/${datasetId}`);
  if (!res.ok) throw new Error("Failed to fetch insights");
  return res.json();
}

export async function runInvestigation(
  datasetId: string,
  question: string,
  focusMetric?: string
): Promise<InvestigationResult> {
  const res = await fetch(`${API_BASE_URL}/investigation/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId, question, focus_metric: focusMetric }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Investigation failed" }));
    throw new Error(err.detail || "Failed to run investigation");
  }
  return res.json();
}

export async function buildDecisionGraph(
  datasetId: string,
  question: string,
  focusMetric?: string
): Promise<DecisionGraphResponse> {
  const res = await fetch(`${API_BASE_URL}/graph/build`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId, question, focus_metric: focusMetric }),
  });
  if (!res.ok) throw new Error("Failed to build decision graph");
  return res.json();
}

export async function runSimulation(params: {
  dataset_id: string;
  target_metric?: string;
  price_change_pct?: number;
  churn_reduction_pct?: number;
  conversion_boost_pct?: number;
  cost_reduction_pct?: number;
}): Promise<SimulationResult> {
  const res = await fetch(`${API_BASE_URL}/simulation/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Simulation failed" }));
    throw new Error(err.detail || "Failed to run simulation");
  }
  return res.json();
}

export async function runSQLQuery(datasetId: string, query: string): Promise<SQLQueryResult> {
  const res = await fetch(`${API_BASE_URL}/analysis/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId, query }),
  });
  return res.json();
}
