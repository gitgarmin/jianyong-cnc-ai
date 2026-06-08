const BASE_URL = 'http://localhost:8000/api';

interface ApiResponse<T = unknown> {
  success: boolean;
  data: T;
  error: string | null;
  metadata: Record<string, unknown> | null;
}

async function request<T>(url: string, options: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);

  const envelope: ApiResponse<T> = await res.json();
  if (!envelope.success) throw new Error(envelope.error ?? '请求失败');

  return envelope.data;
}

export const sendChatMessage = async (message: string) => {
  return request(`${BASE_URL}/chat/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
};

export const saveJobRecord = async (record: Record<string, unknown>) => {
  return request(`${BASE_URL}/records/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(record),
  });
};
