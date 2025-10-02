import Link from "next/link";
import { notFound } from "next/navigation";
import { getServerSession } from "next-auth";

import { ProjectIntakeWorkspace } from "./ProjectIntakeWorkspace";
import { getProject, listRequirements } from "@/lib/api";
import { authOptions } from "@/lib/auth/options";
import { hasRequiredRole } from "@/lib/auth/guards";
import { Roles } from "@/lib/auth/roles";

interface ProjectIntakePageProps {
  params: { id: string };
}

export default async function ProjectIntakePage({ params }: ProjectIntakePageProps) {
  const projectId = Number.parseInt(params.id, 10);
  if (!Number.isFinite(projectId) || projectId <= 0) {
    notFound();
  }

  let project;
  try {
    project = await getProject(projectId);
  } catch (error) {
    console.error(`Failed to load project ${projectId}`, error);
    notFound();
  }

  let initialRequirements = [];
  try {
    initialRequirements = await listRequirements(project.id);
  } catch (error) {
    console.error(`Failed to load requirements for project ${projectId}`, error);
  }

  const session = await getServerSession(authOptions);
  const userRoles = session?.user?.roles ?? [];
  const canExtract = hasRequiredRole(userRoles, [Roles.Client, Roles.Admin, Roles.Lead]);

  return (
    <main className="container flex min-h-screen flex-col gap-8 py-12">
      <header className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Link href="/projects" className="hover:text-primary">
            Projects
          </Link>
          <span>/</span>
          <Link href={`/projects/${project.id}/settings`} className="hover:text-primary">
            {project.name}
          </Link>
          <span>/</span>
          <span>Intake</span>
        </div>
        <h1 className="text-3xl font-semibold">Requirement intake</h1>
        <p className="text-sm text-muted-foreground">
          Route persona conversations through the extractor to populate the backlog automatically.
        </p>
      </header>

      <ProjectIntakeWorkspace
        projectId={project.id}
        projectName={project.name}
        personas={project.personas}
        initialRequirements={initialRequirements}
        canExtract={canExtract}
      />
    </main>
  );
}