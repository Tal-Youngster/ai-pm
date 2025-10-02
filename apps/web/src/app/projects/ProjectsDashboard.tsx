"use client";

import Link from "next/link";
import type { ChangeEvent, FormEvent } from "react";
import { useMemo, useState, useTransition } from "react";

import { Button } from "@/components/ui/button";
import {
  CreateProjectPayload,
  ProjectDetail,
  ProjectSummary,
  createProject
} from "@/lib/api";

interface ProjectsDashboardProps {
  initialProjects: ProjectSummary[];
  organizationId: number;
  clientId: number | null;
  canOpenConsole: boolean;
  canEnterIntake: boolean;
}

interface FormState {
  name: string;
  description: string;
}

const initialFormState: FormState = {
  name: "",
  description: ""
};

function detailToSummary(detail: ProjectDetail): ProjectSummary {
  return {
    id: detail.id,
    name: detail.name,
    description: detail.description,
    status: detail.status,
    organizationId: detail.organizationId,
    clientId: detail.clientId,
    createdAt: detail.createdAt,
    personaCount: detail.personas.length,
    requirementCount: detail.requirementCounts.total
  };
}

export function ProjectsDashboard({
  initialProjects,
  organizationId,
  clientId,
  canOpenConsole,
  canEnterIntake
}: ProjectsDashboardProps) {
  const [projects, setProjects] = useState<ProjectSummary[]>(initialProjects);
  const [formState, setFormState] = useState<FormState>(initialFormState);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const sortedProjects = useMemo(() => {
    return [...projects].sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }, [projects]);

  const defaultProjectId = sortedProjects[0]?.id;
  const defaultIntakeHref = defaultProjectId ? `/projects/${defaultProjectId}/intake` : "/projects";
  const inferredClientId = useMemo(() => {
    if (clientId !== null && clientId !== undefined) {
      return clientId;
    }
    const firstWithClient = sortedProjects.find((project) => project.clientId !== null);
    return firstWithClient?.clientId ?? null;
  }, [clientId, sortedProjects]);

  const handleFieldChange = (field: keyof FormState) => (
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormState((previous) => ({
      ...previous,
      [field]: event.target.value
    }));
  };

  const resetForm = () => {
    setFormState(initialFormState);
  };

  const handleCreateProject = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    if (!formState.name.trim()) {
      setError("Project name is required");
      return;
    }

    const payload: CreateProjectPayload = {
      organizationId,
      name: formState.name.trim(),
      description: formState.description.trim() || undefined,
      clientId: inferredClientId ?? undefined
    };

    startTransition(async () => {
      try {
        const created = await createProject(payload);
        setProjects((previous) => [detailToSummary(created), ...previous]);
        setSuccess(`Created project "${created.name}".`);
        resetForm();
      } catch (creationError) {
        setError(
          creationError instanceof Error ? creationError.message : "Failed to create project"
        );
      }
    });
  };

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-semibold">Projects</h1>
          <p className="text-sm text-muted-foreground">
            Track initiatives, manage cadence, and launch new engagements.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Button asChild variant={canOpenConsole ? "default" : "secondary"} disabled={!canOpenConsole}>
            <Link href={canOpenConsole ? "/console" : "#"}>Open Console</Link>
          </Button>
          <Button asChild variant={canEnterIntake ? "default" : "secondary"}>
            <Link href={canEnterIntake ? defaultIntakeHref : "/projects"}>Enter Intake</Link>
          </Button>
        </div>
      </header>

      <section className="grid gap-6 rounded-lg border bg-card p-6 shadow-sm">
        <div>
          <h2 className="text-xl font-semibold">Create a project</h2>
          <p className="text-sm text-muted-foreground">
            Provide discovery details to spin up a fresh backlog.
          </p>
        </div>
        <form className="grid gap-4 md:grid-cols-2" onSubmit={handleCreateProject}>
          <div className="md:col-span-1">
            <label className="mb-1 block text-sm font-medium" htmlFor="project-name">
              Name
            </label>
            <input
              id="project-name"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Discovery Project"
              value={formState.name}
              onChange={handleFieldChange("name")}
            />
          </div>
          <div className="md:col-span-2">
            <label className="mb-1 block text-sm font-medium" htmlFor="project-description">
              Description
            </label>
            <textarea
              id="project-description"
              className="h-24 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Context, goals, or notes"
              value={formState.description}
              onChange={handleFieldChange("description")}
            />
          </div>
          <div className="md:col-span-2 flex items-center gap-3">
            <Button type="submit" disabled={isPending}>
              {isPending ? "Creating..." : "Create project"}
            </Button>
            {error ? <p className="text-sm text-destructive">{error}</p> : null}
            {success ? <p className="text-sm text-green-600">{success}</p> : null}
          </div>
        </form>
      </section>

      <section className="grid gap-4 rounded-lg border bg-card p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Project roster</h2>
          <span className="text-sm text-muted-foreground">Organization #{organizationId}</span>
        </div>
        {sortedProjects.length === 0 ? (
          <p className="text-sm text-muted-foreground">No projects yet. Create one to get started.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[640px] text-sm">
              <thead className="text-left text-muted-foreground">
                <tr className="border-b">
                  <th className="py-2 pr-4">Name</th>
                  <th className="py-2 pr-4">Status</th>
                  <th className="py-2 pr-4">Personas</th>
                  <th className="py-2 pr-4">Requirements</th>
                  <th className="py-2 pr-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedProjects.map((project) => (
                  <tr key={project.id} className="border-b last:border-0">
                    <td className="py-3 pr-4">
                      <div className="flex flex-col">
                        <span className="font-medium">{project.name}</span>
                        {project.description ? (
                          <span className="text-xs text-muted-foreground">{project.description}</span>
                        ) : null}
                      </div>
                    </td>
                    <td className="py-3 pr-4">
                      <span className="rounded-full bg-muted px-2 py-1 text-xs uppercase tracking-wide">
                        {project.status}
                      </span>
                    </td>
                    <td className="py-3 pr-4">{project.personaCount}</td>
                    <td className="py-3 pr-4">{project.requirementCount}</td>
                    <td className="py-3 pr-4">
                      <div className="flex flex-wrap items-center gap-2">
                        <Button asChild size="sm" variant="outline">
                          <Link href={`/projects/${project.id}/settings`}>Settings</Link>
                        </Button>
                        <Button asChild size="sm" variant="outline">
                          <Link href={`/projects/${project.id}/personas`}>Personas</Link>
                        </Button>
                        <Button
                          asChild
                          size="sm"
                          variant={canOpenConsole ? "default" : "secondary"}
                          disabled={!canOpenConsole}
                        >
                          <Link href={canOpenConsole ? `/console?projectId=${project.id}` : "#"}>
                            Open Console
                          </Link>
                        </Button>
                        <Button
                          asChild
                          size="sm"
                          variant={canEnterIntake ? "default" : "secondary"}
                        >
                          <Link href={`/projects/${project.id}/intake`}>
                            Enter Intake
                          </Link>
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
