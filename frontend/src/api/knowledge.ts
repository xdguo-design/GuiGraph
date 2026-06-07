/** 知识库 API */
import request from './request'

export const knowledgeAPI = {
  // ── 知识库 ──
  listKnowledgeBases: () => request.get('/knowledge/bases'),
  getKnowledgeBase: (kbId: number) =>
    request.get(`/knowledge/bases/${kbId}`),
  createKnowledgeBase: (data: any) =>
    request.post('/knowledge/bases', data),

  // ── 笔记 ──
  listNotes: (params?: { knowledge_base_id?: number; team_id?: number }) =>
    request.get('/knowledge/notes', { params }),
  getNote: (noteId: number) => request.get(`/knowledge/notes/${noteId}`),
  createNote: (data: any) => request.post('/knowledge/notes', data),
  updateNote: (noteId: number, data: any) =>
    request.put(`/knowledge/notes/${noteId}`, data),
  deleteNote: (noteId: number) =>
    request.delete(`/knowledge/notes/${noteId}`),
  aiGenerateNote: (noteId: number) =>
    request.post(`/knowledge/notes/${noteId}/ai-generate`),

  // ── 版本历史 ──
  listNoteVersions: (noteId: number) =>
    request.get(`/knowledge/notes/${noteId}/versions`),
}
