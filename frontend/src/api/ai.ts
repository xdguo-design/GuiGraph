/** AI 模块 API */
import request from './request'

export const aiAPI = {
  // ── RAG 搜索 ──
  ragSearch: (query: string, top_k = 5) =>
    request.post('/ai/rag/search', { query, top_k }),

  ragAnalyze: (document: string) =>
    request.post('/ai/rag/analyze', { document }),

  generateSummary: (content: string) =>
    request.post('/ai/generate/summary', { content }),

  // ── 模型管理 ──
  listModels: (tier?: string) =>
    request.get('/ai/models', { params: tier ? { tier } : {} }),
  createModel: (data: any) => request.post('/ai/models', data),
  updateModel: (modelId: number | string, data: any) =>
    request.put(`/ai/models/${modelId}`, data),
  deleteModel: (modelId: number | string) =>
    request.delete(`/ai/models/${modelId}`),

  // ── 场景绑定 ──
  listScenarios: () => request.get('/ai/models/scenarios'),
  createScenario: (data: any) => request.post('/ai/models/scenarios', data),
  updateScenario: (bindingId: number | string, data: any) =>
    request.put(`/ai/models/scenarios/${bindingId}`, data),
  deleteScenario: (bindingId: number | string) =>
    request.delete(`/ai/models/scenarios/${bindingId}`),

  // ── Prompt 模板 ──
  listPrompts: () => request.get('/ai/models/prompts'),
  createPrompt: (data: any) => request.post('/ai/models/prompts', data),
  updatePrompt: (templateId: number | string, data: any) =>
    request.put(`/ai/models/prompts/${templateId}`, data),

  // ── 用量统计 ──
  getUsage: () => request.get('/ai/models/usage'),
  getUsageLogs: (limit = 50) => request.get('/ai/models/usage/logs', { params: { limit } }),

  // ── Skill 管理 ──
  listSkills: () => request.get('/ai/skills'),
  enableSkill: (skillId: number) =>
    request.post(`/ai/skills/${skillId}/enable`),
  disableSkill: (skillId: number) =>
    request.post(`/ai/skills/${skillId}/disable`),

  // ── MCP 管理 ──
  listMcpServers: () => request.get('/ai/mcp'),
  registerMcp: (data: any) => request.post('/ai/mcp', data),
  updateMcp: (mcpId: number, data: any) =>
    request.put(`/ai/mcp/${mcpId}`, data),
  deleteMcp: (mcpId: number) => request.delete(`/ai/mcp/${mcpId}`),
  testMcpConnection: (mcpId: number) =>
    request.post(`/ai/mcp/${mcpId}/connect`),
  getMcpTools: (mcpId: number) =>
    request.get(`/ai/mcp/${mcpId}/tools`),
}
