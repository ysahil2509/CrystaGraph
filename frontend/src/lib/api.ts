/**
 * CrystaGraph API Client
 * Provides typed HTTP communication with the FastAPI microservice.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface UserProfile {
  user_id: string;
  email: string;
  full_name: string;
  institution?: string;
  department?: string;
  role?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserProfile;
}

export interface WorkspaceSummary {
  counts: {
    papers: number;
    tables: number;
    materials: number;
    compositions: number;
    properties: number;
    knowledge_triples: number;
  };
  recent_papers: Array<{
    paper_id: string;
    doi: string;
    title: string;
    status: string;
  }>;
  recent_jobs: Array<{
    job_id: string;
    filename: string;
    file_type: string;
    status: string;
    progress_pct: number;
    current_step: string;
    created_at: string;
  }>;
  active_user: string;
}

export interface JobStatusResponse {
  job_id: string;
  user_id?: string;
  paper_id?: string;
  filename: string;
  file_type: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress_pct: number;
  current_step: string;
  extracted_tables_count: number;
  extracted_compositions_count: number;
  extracted_properties_count: number;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("crystagraph_token");
}

export function setAuthSession(token: string, user: UserProfile): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("crystagraph_token", token);
  localStorage.setItem("crystagraph_user", JSON.stringify(user));
}

export function clearAuthSession(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("crystagraph_token");
  localStorage.removeItem("crystagraph_user");
}

export function getStoredUser(): UserProfile | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("crystagraph_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = "API request failed";
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || errorDetail;
    } catch {
      errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

// Authentication API
export async function loginUser(email: string, password: string): Promise<AuthResponse> {
  const data = await request<AuthResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setAuthSession(data.access_token, data.user);
  return data;
}

export async function registerUser(payload: {
  email: string;
  password: string;
  full_name: string;
  institution?: string;
  department?: string;
  role?: string;
}): Promise<AuthResponse> {
  const data = await request<AuthResponse>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  setAuthSession(data.access_token, data.user);
  return data;
}

export async function getCurrentUser(): Promise<UserProfile> {
  return request<UserProfile>("/api/v1/auth/me");
}

// Workspace API
export async function getWorkspaceSummary(): Promise<WorkspaceSummary> {
  return request<WorkspaceSummary>("/api/v1/workspace/summary");
}

export async function listWorkspaces(): Promise<Array<{
  workspace_id: string;
  title: string;
  description: string;
  created_at: string;
}>> {
  return request("/api/v1/workspaces");
}

export async function createWorkspace(title: string, description: string = ""): Promise<{
  workspace_id: string;
  title: string;
  description: string;
}> {
  return request("/api/v1/workspaces", {
    method: "POST",
    body: JSON.stringify({ title, description }),
  });
}

// Papers & Tables API
export async function listPapers(): Promise<Array<{
  paper_id: string;
  doi: string;
  pii: string;
  title: string;
  status: string;
}>> {
  return request("/api/v1/papers");
}

export async function getPaperDetail(paperId: string): Promise<{
  paper_id: string;
  doi: string;
  pii: string;
  title: string;
  abstract: string;
  source_file: string;
  status: string;
  tables: Array<{
    table_id: string;
    caption: string;
    footnote: string;
    num_rows: number;
    num_cols: number;
  }>;
}> {
  return request(`/api/v1/papers/${paperId}`);
}

export async function getTableDetail(tableId: string): Promise<{
  table_id: string;
  paper_id: string;
  caption: string;
  footnote: string;
  num_rows: number;
  num_cols: number;
  headers: string[];
  raw_records: Array<Record<string, unknown>>;
  cleaned_records: Array<Record<string, unknown>>;
}> {
  return request(`/api/v1/tables/${tableId}`);
}

// Search & Prediction API
export async function searchKnowledge(q?: string, property?: string): Promise<{
  count: number;
  results: Array<Record<string, unknown>>;
}> {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (property) params.set("property", property);
  const queryStr = params.toString() ? `?${params.toString()}` : "";
  return request(`/api/v1/search${queryStr}`);
}

export async function predictProperty(
  propertyName: string,
  composition: Record<string, number>
): Promise<{
  property: string;
  predicted_value: number;
  standard_unit: string;
  r2_score: number;
  confidence_interval_95: [number, number];
  features_used: Record<string, number>;
  top_influencing_elements: Array<{ element: string; importance: number }>;
}> {
  return request("/api/v1/predict", {
    method: "POST",
    body: JSON.stringify({ property_name: propertyName, composition }),
  });
}

// Paper Upload & Job Tracking API
export async function uploadPaper(
  file: File,
  options: {
    extract_tables?: boolean;
    extract_compositions?: boolean;
    extract_properties?: boolean;
    extract_text?: boolean;
    normalize_si?: boolean;
  } = {}
): Promise<JobStatusResponse> {
  const token = getAuthToken();
  const formData = new FormData();
  formData.append("file", file);
  formData.append("extract_tables", String(options.extract_tables ?? true));
  formData.append("extract_compositions", String(options.extract_compositions ?? true));
  formData.append("extract_properties", String(options.extract_properties ?? true));
  formData.append("extract_text", String(options.extract_text ?? true));
  formData.append("normalize_si", String(options.normalize_si ?? true));

  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/papers/upload`, {
    method: "POST",
    headers,
    body: formData,
  });

  if (!response.ok) {
    let errorDetail = "Failed to upload document";
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errorDetail;
    } catch {
      errorDetail = `HTTP ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  return request<JobStatusResponse>(`/api/v1/jobs/${jobId}`);
}

export async function listJobs(): Promise<Array<JobStatusResponse>> {
  return request<Array<JobStatusResponse>>("/api/v1/jobs");
}

export async function listAllTables(): Promise<Array<{
  table_id: string;
  paper_id: string;
  caption: string;
  footnote: string;
  num_rows: number;
  num_cols: number;
  paper_title?: string;
  doi?: string;
}>> {
  return request("/api/v1/tables");
}

export async function listAllProperties(params?: {
  category?: string;
  property_name?: string;
}): Promise<Array<{
  prop_id: number;
  material_name: string;
  property_name: string;
  property_category: string;
  value_numeric: number;
  value_raw: string;
  unit: string;
  si_value: number;
  si_unit: string;
  source_type: string;
  condition_footnote?: string;
  paper_id: string;
  table_id: string;
  doi: string;
}>> {
  const q = new URLSearchParams();
  if (params?.category) q.set("category", params.category);
  if (params?.property_name) q.set("property_name", params.property_name);
  const qStr = q.toString() ? `?${q.toString()}` : "";
  return request(`/api/v1/properties${qStr}`);
}

export async function recordTableCorrection(
  tableId: string,
  payload: {
    paper_id: string;
    record_type: string;
    target_id?: string;
    field_name: string;
    original_value?: string;
    corrected_value: string;
    academic_notes?: string;
  }
): Promise<{ status: string; message: string }> {
  return request(`/api/v1/tables/${tableId}/correct`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getSynthesisData(): Promise<{
  total_records: number;
  materials_count: number;
  papers_count: number;
  records: Array<Record<string, unknown>>;
  ashby_points: Array<{
    material: string;
    paper_id: string;
    doi: string;
    yield_strength_mpa?: number;
    density_gcm3?: number;
    tensile_strength_mpa?: number;
    hardness_hv?: number;
  }>;
}> {
  return request("/api/v1/synthesize");
}

export async function sendChatMessage(message: string): Promise<{
  response: string;
  citations: Array<{
    paper_id: string;
    doi: string;
    table_id: string;
    material?: string;
    property?: string;
  }>;
  grounded: boolean;
  match_count: number;
}> {
  return request("/api/v1/assistant/chat", {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}
