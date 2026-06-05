const BASE_URL = 'http://localhost:8000/api';

export const sendChatMessage = async (message: string) => {
  const res = await fetch(`${BASE_URL}/chat/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error('Network response was not ok');
  return res.json();
};

export const saveJobRecord = async (record: any) => {
  const res = await fetch(`${BASE_URL}/records/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(record),
  });
  return res.json();
};
