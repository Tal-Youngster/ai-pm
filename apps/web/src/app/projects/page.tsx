import { getServerSession } from "next-auth";

import { ProjectsDashboard } from "./ProjectsDashboard";
import { getProjects, type ProjectSummary } from "@/lib/api";
import { authOptions } from "@/lib/auth/options";
import { hasRequiredRole } from "@/lib/auth/guards";
import { Roles } from "@/lib/auth/roles";

type SearchParams = Record<string, string | string[] | undefined>;

function coerceParam(value: string | string[] | undefined) {
  if (Array.isArray(value)) {
    return value[0];
  }
  return value;
}

function parseOrganizationId(searchParams: SearchParams): number {
  const defaultId = Number.parseInt(process.env.NEXT_PUBLIC_DEFAULT_ORGANIZATION_ID ?? "1", 10) || 1;
  const candidate = coerceParam(searchParams.organizationId ?? searchParams.organization_id);

  if (!candidate) {
    return defaultId;
  }

  const parsed = Number.parseInt(candidate ?? "", 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : defaultId;
}

function parseClientId(searchParams: SearchParams): number | null {
  const candidate = coerceParam(searchParams.clientId ?? searchParams.client_id);
  if (!candidate) {
    return null;
  }

  const parsed = Number.parseInt(candidate, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
}

interface ProjectsPageProps {
  searchParams: SearchParams;
}

export default async function ProjectsPage({ searchParams }: ProjectsPageProps) {
  const session = await getServerSession(authOptions);
  const organizationId = parseOrganizationId(searchParams);
  const clientId = parseClientId(searchParams);

  let initialProjects: ProjectSummary[] = [];
  try {
    initialProjects = await getProjects({ organizationId, clientId: clientId ?? undefined });
  } catch (error) {
    console.error("Failed to load projects", error);
  }

  const userRoles = session?.user?.roles ?? [];
  const canOpenConsole = hasRequiredRole(userRoles, [Roles.Admin, Roles.Lead]);
  const canEnterIntake = hasRequiredRole(userRoles, Roles.Client);

  return (
    <main className="container flex min-h-screen flex-col gap-8 py-12">
      <ProjectsDashboard
        initialProjects={initialProjects}
        organizationId={organizationId}
        clientId={clientId}
        canOpenConsole={canOpenConsole}
        canEnterIntake={canEnterIntake}
      />
    </main>
  );
}
