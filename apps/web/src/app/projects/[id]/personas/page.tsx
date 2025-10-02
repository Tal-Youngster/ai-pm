import Link from "next/link";
import { notFound } from "next/navigation";
import { getServerSession } from "next-auth";

import { ProjectPersonasManager } from "./ProjectPersonasManager";
import { getProject } from "@/lib/api";
import { authOptions } from "@/lib/auth/options";
import { hasRequiredRole } from "@/lib/auth/guards";
import { Roles } from "@/lib/auth/roles";

interface ProjectPersonasPageProps {
  params: { id: string };
}

export default async function ProjectPersonasPage({ params }: ProjectPersonasPageProps) {
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

  const session = await getServerSession(authOptions);
  const userRoles = session?.user?.roles ?? [];
  const canManage = hasRequiredRole(userRoles, [Roles.Admin, Roles.Lead]);

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
          <span>Personas</span>
        </div>
        <h1 className="text-3xl font-semibold">Project personas</h1>
        <p className="text-sm text-muted-foreground">
          Manage the voices connected to this project so intake stays grounded in real stakeholders.
        </p>
      </header>

      <ProjectPersonasManager
        projectId={project.id}
        projectName={project.name}
        initialPersonas={project.personas}
        canManage={canManage}
      />
    </main>
  );
}