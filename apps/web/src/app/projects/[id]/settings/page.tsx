import Link from "next/link";
import { notFound } from "next/navigation";
import { getServerSession } from "next-auth";

import { ProjectSettingsForm } from "./ProjectSettingsForm";
import { getProject } from "@/lib/api";
import { authOptions } from "@/lib/auth/options";
import { hasRequiredRole } from "@/lib/auth/guards";
import { Roles } from "@/lib/auth/roles";

interface ProjectSettingsPageProps {
  params: { id: string };
}

export default async function ProjectSettingsPage({ params }: ProjectSettingsPageProps) {
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
  const canManage = hasRequiredRole(session?.user?.roles ?? [], [Roles.Admin, Roles.Lead]);

  return (
    <main className="container flex min-h-screen flex-col gap-8 py-12">
      <header className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Link href="/projects" className="hover:text-primary">
            Projects
          </Link>
          <span>/</span>
          <span>{project.name}</span>
        </div>
        <h1 className="text-3xl font-semibold">Project settings</h1>
        <p className="text-sm text-muted-foreground">
          Manage lifecycle controls, update milestones, and clean up linked artifacts.
        </p>
      </header>
      <ProjectSettingsForm project={project} canManage={canManage} />
    </main>
  );
}
