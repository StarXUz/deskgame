import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
  timeout: 20000
})

export function errorText(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (detail?.errors) return detail.errors.join('\n')
    return error.message
  }
  return String(error)
}
