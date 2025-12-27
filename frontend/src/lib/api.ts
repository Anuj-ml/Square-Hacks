const API_BASE_URL = (import.meta.env?.VITE_API_URL as string) || 'http://localhost:8000';

export async function fetchBeds(department?: string) {
  const url = department 
    ? `${API_BASE_URL}/api/v1/beds?department=${department}` 
    : `${API_BASE_URL}/api/v1/beds`;
  const response = await fetch(url);
  return response.json();
}

export async function fetchStaff(shift?: string) {
  const url = shift
    ? `${API_BASE_URL}/api/v1/staff?shift=${shift}` 
    : `${API_BASE_URL}/api/v1/staff`;
  const response = await fetch(url);
  return response.json();
}

export async function fetchInventory(criticalOnly: boolean = false) {
  const url = `${API_BASE_URL}/api/v1/inventory?critical_only=${criticalOnly}`;
  const response = await fetch(url);
  return response.json();
}

export async function fetchLatestPrediction() {
  const response = await fetch(`${API_BASE_URL}/api/v1/predictions/latest`);
  return response.json();
}

export async function fetchRecommendations(status?: string) {
  const url = status
    ? `${API_BASE_URL}/api/v1/recommendations?status=${status}` 
    : `${API_BASE_URL}/api/v1/recommendations`;
  const response = await fetch(url);
  return response.json();
}

export async function approveRecommendation(recId: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/recommendations/${recId}/approve`, {
    method: 'POST'
  });
  return response.json();
}

export async function rejectRecommendation(recId: string, reason: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/recommendations/${recId}/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason })
  });
  return response.json();
}

export async function getCostSavings() {
  const response = await fetch(`${API_BASE_URL}/api/v1/analytics/cost-savings`);
  return response.json();
}

export async function triggerCrisisSimulation(crisisType: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/simulation/trigger-crisis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ crisis_type: crisisType })
  });
  return response.json();
}

export async function fetchCurrentAQI(lat?: number, lon?: number, city?: string) {
  let url = `${API_BASE_URL}/api/v1/environment/aqi`;
  const params = new URLSearchParams();
  
  if (lat !== undefined && lon !== undefined) {
    params.append('lat', lat.toString());
    params.append('lon', lon.toString());
  } else if (city) {
    params.append('city', city);
  }
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await fetch(url);
  return response.json();
}

// ============================================
// RAG CHATBOT API
// ============================================

export interface RagQueryRequest {
  question: string;
  context?: {
    aqi?: number;
    bed_capacity?: number;
    active_alerts?: number;
  };
}

export interface RagResponse {
  answer: string;
  sources: Array<{
    id: string;
    content: string;
    metadata: Record<string, any>;
  }>;
  confidence: number;
  mode: 'rag' | 'offline' | 'no_documents' | 'error';
  context_used?: boolean;
  error?: string;
}

export interface RagStatus {
  status: 'healthy' | 'unhealthy' | 'error';
  initialized: boolean;
  document_count: number;
  database_connected: boolean;
  error?: string;
}

export async function queryRagChatbot(request: RagQueryRequest): Promise<RagResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/rag/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  
  if (!response.ok) {
    throw new Error(`RAG query failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getRagStatus(): Promise<RagStatus> {
  const response = await fetch(`${API_BASE_URL}/api/v1/rag/status`);
  return response.json();
}

export async function ingestRagDocuments(documents: Array<Record<string, any>>) {
  const response = await fetch(`${API_BASE_URL}/api/v1/rag/ingest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ documents })
  });
  
  if (!response.ok) {
    throw new Error(`RAG ingestion failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function translateText(text: string, targetLang: string): Promise<string> {
  try {
    if (!text || targetLang === 'en') return text;
    
    console.log('🌐 Translating:', text.substring(0, 50) + '...', 'to', targetLang);
    
    const params = new URLSearchParams({
      text: text,
      target_lang: targetLang
    });
    
    const response = await fetch(`${API_BASE_URL}/api/v1/translate?${params.toString()}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    if (!response.ok) {
      throw new Error(`Translation failed: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('✅ Translated:', data.translated?.substring(0, 50) + '...');
    return data.translated || text;
  } catch (error) {
    console.error('❌ Translation error:', error);
    return text;
  }
}
