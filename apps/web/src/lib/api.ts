const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export interface HealthResponse {
  status: string;
  message?: string;
  [key: string]: unknown;
}

export type ProjectStatus = "planned" | "active" | "paused" | "completed" | "archived";
export type PersonaRole = "client" | "lead" | "developer" | "pm_agent";
export type RequirementType = "feature" | "bug" | "improvement" | "constraint";

export const PERSONA_ROLE_OPTIONS: PersonaRole[] = [
  "client",
  "lead",
  "developer",
  "pm_agent"
];

export interface ProjectBase {
  id: number;
  name: string;
  description: string | null;
  status: ProjectStatus;
  organizationId: number;
  clientId: number | null;
  createdAt: string;
}

export interface ProjectSummary extends ProjectBase {
  personaCount: number;
  requirementCount: number;
}

export interface PersonaSummary {
  id: string;
  role: PersonaRole;
  displayName: string;
}

export interface Persona extends PersonaSummary {
  projectId: number;
  userId: number | null;
  createdAt: string;
  updatedAt: string;
}

export interface RequirementCounts {
  total: number;
  byType: Record<string, number>;
}

export interface Requirement {
  id: string;
  projectId: number;
  personaId: string;
  text: string;
  type: RequirementType;
  confidence: number | null;
  clusterId: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface ProjectDetail extends ProjectBase {
  personas: PersonaSummary[];
  requirementCounts: RequirementCounts;
}

export interface CreateProjectPayload {
  organizationId: number;
  name: string;
  description?: string;
  clientId?: number | null;
  status?: ProjectStatus;
}

export interface UpdateProjectPayload {
  name?: string;
  description?: string | null;
  status?: ProjectStatus;
}

export interface CreatePersonaPayload {
  projectId: number;
  role: PersonaRole;
  displayName: string;
  userId?: number | null;
}

export interface UpdatePersonaPayload {
  role?: PersonaRole;
  displayName?: string;
}

export interface IntakeExtractPayload {
  projectId: number;
  personaId: string;
  text: string;
}

export interface UpdateRequirementPayload {
  type?: RequirementType;
  confidence?: number | null;
}

type JsonRecord = Record<string, unknown>;

type RequestOptions = RequestInit & { cache?: RequestCache };

function buildUrl(path: string) {
  const base = API_BASE_URL.replace(/\/$/, "");
  if (!base) {
    return path;
  }

  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

function removeUndefined<T extends JsonRecord>(input: T): JsonRecord {
  return Object.fromEntries(
    Object.entries(input).filter(([, value]) => value !== undefined)
  );
}

async function requestJson<T>(path: string, init?: RequestOptions): Promise<T> {
  const response = await fetch(buildUrl(path), {
    cache: "no-store",
    headers: {
      Accept: "application/json",
      ...(init?.headers ?? {})
    },
    ...init
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(`Request failed with status ${response.status}: ${message}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

function normalizeProjectBase(dto: JsonRecord): ProjectBase {
  return {
    id: dto.id as number,
    name: dto.name as string,
    description: (dto.description as string | null) ?? null,
    status: (dto.status as ProjectStatus) ?? "active",
    organizationId: dto.organization_id as number,
    clientId: (dto.client_id as number | null) ?? null,
    createdAt: dto.created_at as string
  };
}

function normalizePersonaSummary(dto: JsonRecord): PersonaSummary {
  return {
    id: dto.id as string,
    role: (dto.role as PersonaRole) ?? "client",
    displayName: (dto.display_name as string | undefined) ?? (dto.displayName as string)
  };
}

function normalizePersona(dto: JsonRecord): Persona {
  const summary = normalizePersonaSummary(dto);
  return {
    ...summary,
    projectId: dto.project_id as number,
    userId: (dto.user_id as number | null) ?? null,
    createdAt: dto.created_at as string,
    updatedAt: dto.updated_at as string
  };
}

function normalizeProjectSummary(dto: JsonRecord): ProjectSummary {
  const base = normalizeProjectBase(dto);
  return {
    ...base,
    personaCount: (dto.persona_count as number | null) ?? 0,
    requirementCount: (dto.requirement_count as number | null) ?? 0
  };
}

function normalizeProjectDetail(dto: JsonRecord): ProjectDetail {
  const base = normalizeProjectBase(dto);
  const personas = Array.isArray(dto.personas)
    ? dto.personas.map((persona) => normalizePersonaSummary(persona as JsonRecord))
    : [];
  const requirementCountsDto = (dto.requirement_counts ?? {}) as JsonRecord;
  return {
    ...base,
    personas,
    requirementCounts: {
      total: (requirementCountsDto.total as number | null) ?? 0,
      byType: (requirementCountsDto.by_type as Record<string, number> | undefined) ?? {}
    }
  };
}

function normalizeRequirement(dto: JsonRecord): Requirement {
  return {
    id: dto.id as string,
    projectId: dto.project_id as number,
    personaId: dto.persona_id as string,
    text: dto.text as string,
    type: (dto.type as RequirementType) ?? "feature",
    confidence: (dto.confidence as number | null) ?? null,
    clusterId: (dto.cluster_id as string | null) ?? null,
    createdAt: dto.created_at as string,
    updatedAt: dto.updated_at as string
  };
}

export async function getApiHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>("/v1/ping");
}

export interface GetProjectsParams {
  organizationId: number;
  clientId?: number;
  userId?: number;
}

export async function getProjects(params: GetProjectsParams): Promise<ProjectSummary[]> {
  const search = new URLSearchParams({
    organization_id: String(params.organizationId)
  });

  if (params.clientId !== undefined) {
    search.set("client_id", String(params.clientId));
  }

  if (params.userId !== undefined) {
    search.set("user_id", String(params.userId));
  }

  const response = await requestJson<JsonRecord[]>(`/v1/projects?${search.toString()}`);
  return response.map((project) => normalizeProjectSummary(project));
}

export async function createProject(payload: CreateProjectPayload): Promise<ProjectDetail> {
  const body = removeUndefined({
    name: payload.name,
    description: payload.description,
    organization_id: payload.organizationId,
    client_id: payload.clientId ?? null,
    status: payload.status
  });

  const response = await requestJson<JsonRecord>("/v1/projects", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });

  return normalizeProjectDetail(response);
}

export async function getProject(projectId: number): Promise<ProjectDetail> {
  const response = await requestJson<JsonRecord>(`/v1/projects/${projectId}`);
  return normalizeProjectDetail(response);
}

export async function updateProject(
  projectId: number,
  payload: UpdateProjectPayload
): Promise<ProjectDetail> {
  const body = removeUndefined({
    name: payload.name,
    description: payload.description,
    status: payload.status
  });

  const response = await requestJson<JsonRecord>(`/v1/projects/${projectId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });

  return normalizeProjectDetail(response);
}

export async function deleteProject(projectId: number): Promise<void> {
  await requestJson(`/v1/projects/${projectId}`, {
    method: "DELETE"
  });
}

export async function listPersonas(projectId: number): Promise<Persona[]> {
  const search = new URLSearchParams({ project_id: String(projectId) });
  const response = await requestJson<JsonRecord[]>(`/v1/personas?${search.toString()}`);
  return response.map((persona) => normalizePersona(persona));
}

export async function createPersona(payload: CreatePersonaPayload): Promise<Persona> {
  const body = removeUndefined({
    project_id: payload.projectId,
    role: payload.role,
    display_name: payload.displayName,
    user_id: payload.userId ?? undefined
  });

  const response = await requestJson<JsonRecord>("/v1/personas", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });

  return normalizePersona(response);
}

export async function updatePersona(
  personaId: string,
  payload: UpdatePersonaPayload
): Promise<Persona> {
  const body = removeUndefined({
    role: payload.role,
    display_name: payload.displayName
  });

  const response = await requestJson<JsonRecord>(`/v1/personas/${personaId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });

  return normalizePersona(response);
}

export async function deletePersona(personaId: string): Promise<void> {
  await requestJson(`/v1/personas/${personaId}`, {
    method: "DELETE"
  });
}

export async function listRequirements(
  projectId: number,
  personaId?: string
): Promise<Requirement[]> {
  const search = new URLSearchParams({ project_id: String(projectId) });
  if (personaId) {
    search.set("persona_id", personaId);
  }

  const response = await requestJson<JsonRecord[]>(`/v1/requirements?${search.toString()}`);
  return response.map((requirement) => normalizeRequirement(requirement));
}

export async function extractRequirements(
  payload: IntakeExtractPayload
): Promise<Requirement[]> {
  const body = {
    project_id: payload.projectId,
    persona_id: payload.personaId,
    text: payload.text
  };

  const response = await requestJson<JsonRecord[]>("/v1/intake/extract", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });

  return response.map((requirement) => normalizeRequirement(requirement));
}

export async function updateRequirement(
  requirementId: string,
  payload: UpdateRequirementPayload
): Promise<Requirement> {
  const body = removeUndefined({
    type: payload.type,
    confidence: payload.confidence
  });

  const response = await requestJson<JsonRecord>(`/v1/requirements/${requirementId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });

  return normalizeRequirement(response);
}




