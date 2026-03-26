const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options)
  const contentType = response.headers.get('content-type') || ''
  const isJson = contentType.includes('application/json')
  const data = isJson ? await response.json() : await response.text()

  if (!response.ok) {
    const detail = typeof data === 'object' && data?.detail ? data.detail : data
    throw new Error(String(detail || 'Erro na API'))
  }

  return data
}

export async function fetchCities() {
  const data = await request('/cities')
  return data.cities ?? []
}

export async function fetchModels() {
  const data = await request('/models')
  return data.models ?? []
}

export async function validatePlate(plate) {
  return request('/auth/plate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ plate }),
  })
}

export async function detectPlateFromImage(file) {
  const form = new FormData()
  form.append('file', file)
  return request('/auth/plate-ocr', {
    method: 'POST',
    body: form,
  })
}

export async function runRoute(payload) {
  return request('/route', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export async function runCompare(payload) {
  return request('/route/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export async function fetchAttractions(payload) {
  return request('/attractions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}
