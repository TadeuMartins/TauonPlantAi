
import axios from 'axios'

const base = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const key = localStorage.getItem('TAUON_API_KEY') || 'dev-key'

export async function ingestFolderUpload(files: File[]) {
  const form = new FormData()
  form.append('x_api_key', key)
  files.forEach(f => form.append('files', f))
  return axios.post(`${base}/ingest/folder-upload`, form)
}

export async function ingestSharePoint(sp_folder: string) {
  const form = new FormData()
  form.append('x_api_key', key)
  form.append('sp_folder', sp_folder)
  return axios.post(`${base}/ingest/sharepoint`, form)
}

export async function chat(question: string) {
  const form = new FormData()
  form.append('x_api_key', key)
  form.append('question', question)
  const { data } = await axios.post(`${base}/chat`, form)
  return data
}
