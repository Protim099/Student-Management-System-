// ----------------------------------------------------------------------
// API Base URL - backend যেখানে চলছে সেই ঠিকানা
// ----------------------------------------------------------------------
const API_BASE_URL = 'http://localhost:5000/api';

function getToken() {
  return localStorage.getItem('access_token');
}

function setToken(token) {
  localStorage.setItem('access_token', token);
}

function clearAuth() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
}

function getUser() {
  const u = localStorage.getItem('user');
  return u ? JSON.parse(u) : null;
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = 'index.html';
  }
}

// সাধারণ fetch wrapper - প্রতিটা প্রোটেক্টেড কলে Authorization header যোগ করে
async function apiRequest(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await res.json().catch(() => ({}));

  if (res.status === 401) {
    clearAuth();
    window.location.href = 'index.html';
    return Promise.reject(data);
  }

  if (!res.ok) {
    return Promise.reject(data);
  }

  return data;
}

// ---- Auth ----
async function loginUser(username, password) {
  return apiRequest('/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

async function registerUser(username, email, password) {
  return apiRequest('/register', {
    method: 'POST',
    body: JSON.stringify({ username, email, password }),
  });
}

// ---- Students ----
async function fetchStudents(query = '', page = 1) {
  const params = new URLSearchParams({ page });
  if (query) params.append('q', query);
  return apiRequest(`/students?${params.toString()}`);
}

async function createStudent(payload) {
  return apiRequest('/students', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

async function updateStudent(id, payload) {
  return apiRequest(`/students/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

async function deleteStudent(id) {
  return apiRequest(`/students/${id}`, { method: 'DELETE' });
}

async function fetchStats() {
  return apiRequest('/stats');
}
