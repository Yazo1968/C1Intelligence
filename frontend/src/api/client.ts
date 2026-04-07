import { API_BASE_URL } from '../config';
import { supabase } from '../auth/supabase';
import type { ApiError } from './types';

class ApiClientError extends Error {
  errorCode: string;
  documentId?: string;
  queryId?: string;

  constructor(errorCode: string, message: string, documentId?: string, queryId?: string) {
    super(message);
    this.name = 'ApiClientError';
    this.errorCode = errorCode;
    this.documentId = documentId;
    this.queryId = queryId;
  }
}

async function getAuthHeaders(): Promise<Record<string, string>> {
  const { data: { session } } = await supabase.auth.getSession();
  if (!session?.access_token) {
    throw new ApiClientError('NO_SESSION', 'Not authenticated');
  }
  return { Authorization: `Bearer ${session.access_token}` };
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (response.status === 401) {
    await supabase.auth.signOut();
    window.location.href = '/login';
    throw new ApiClientError('UNAUTHORIZED', 'Session expired');
  }

  if (!response.ok) {
    let errorBody: ApiError;
    try {
      errorBody = await response.json();
    } catch {
      throw new ApiClientError('UNKNOWN', `Request failed with status ${response.status}`);
    }
    throw new ApiClientError(
      errorBody.error_code ?? `HTTP_${response.status}`,
      (() => {
        if (errorBody.message) return errorBody.message;
        const detail = (errorBody as unknown as Record<string, unknown>).detail;
        if (typeof detail === 'string') return detail;
        if (detail && typeof detail === 'object' && 'message' in (detail as object)) {
          return (detail as Record<string, unknown>).message as string;
        }
        return `Request failed with status ${response.status}`;
      })(),
      errorBody.document_id,
      errorBody.query_id,
    );
  }

  return response.json();
}

export const apiClient = {
  async get<T>(path: string): Promise<T> {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}${path}`, { headers });
    return handleResponse<T>(response);
  },

  async post<T>(path: string, body: Record<string, unknown>): Promise<T> {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return handleResponse<T>(response);
  },

  async patch<T>(path: string, body: Record<string, unknown>): Promise<T> {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'PATCH',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return handleResponse<T>(response);
  },

  async postFormData<T>(path: string, formData: FormData): Promise<T> {
    const headers = await getAuthHeaders();
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'POST',
      headers,
      body: formData,
    });
    return handleResponse<T>(response);
  },
};

export { ApiClientError };
