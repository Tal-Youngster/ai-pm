"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { ChangeEvent, FormEvent } from "react";
import { useState, useTransition } from "react";

import { Button } from "@/components/ui/button";
import {
  ProjectDetail,
  ProjectStatus,
  UpdateProjectPayload,
  deleteProject,
  updateProject
} from "@/lib/api";

interface ProjectSettingsFormProps {
  project: ProjectDetail;
  canManage: boolean;
}

interface ProjectFormState {
  name: string;
  description: string;
  status: ProjectStatus;
}

const STATUS_OPTIONS: ProjectStatus[] = [
  "planned",
  "active",
  "paused",
  "completed",
  "archived"
];


export function ProjectSettingsForm({ project, canManage }: ProjectSettingsFormProps) {
  const router = useRouter();
  const [currentProject, setCurrentProject] = useState<ProjectDetail>(project);
  const [formState, setFormState] = useState<ProjectFormState>({
    name: project.name,
    description: project.description ?? "",
    status: project.status
  });
  const [isUpdating, startUpdate] = useTransition();
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFieldChange = (field: keyof ProjectFormState) => (
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    setFormState((previous) => ({
      ...previous,
      [field]: event.target.value
    }));
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    if (!canManage) {
      return;
    }

    const updates: UpdateProjectPayload = {};

    if (formState.name.trim() !== currentProject.name) {
      updates.name = formState.name.trim();
    }

    if ((formState.description.trim() || null) !== (currentProject.description ?? null)) {
      updates.description = formState.description.trim() || null;
    }

    if (formState.status !== currentProject.status) {
      updates.status = formState.status;
    }


    if (Object.keys(updates).length === 0) {
      setSuccess("No changes detected");
      return;
    }

    startUpdate(async () => {
      try {
        const updated = await updateProject(currentProject.id, updates);
        setCurrentProject(updated);
        setFormState({
          name: updated.name,
          description: updated.description ?? "",
          status: updated.status
        });
        setSuccess("Project updated successfully");
      } catch (updateError) {
        setError(updateError instanceof Error ? updateError.message : "Failed to update project");
      }
    });
  };

  const handleDelete = async () => {
    if (!canManage) {
      return;
    }

    const confirmed = window.confirm(
      `Are you sure you want to delete "${currentProject.name}"? This action cannot be undone.`
    );
    if (!confirmed) {
      return;
    }

    setError(null);
    setSuccess(null);
    setIsDeleting(true);
    try {
      await deleteProject(currentProject.id);
      router.replace("/projects");
      router.refresh();
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Failed to delete project");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <form className="grid gap-6" onSubmit={handleSubmit}>
      <section className="grid gap-4 rounded-lg border bg-card p-6 shadow-sm">
        <div>
          <h2 className="text-xl font-semibold">Project metadata</h2>
          <p className="text-sm text-muted-foreground">
            Update core details for this engagement.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium" htmlFor="project-name">
              Name
            </label>
            <input
              id="project-name"
              disabled={!canManage}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:cursor-not-allowed"
              value={formState.name}
              onChange={handleFieldChange("name")}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium" htmlFor="project-status">
              Status
            </label>
            <select
              id="project-status"
              disabled={!canManage}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:cursor-not-allowed"
              value={formState.status}
              onChange={handleFieldChange("status")}
            >
              {STATUS_OPTIONS.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </div>
          <div className="md:col-span-2">
            <label className="mb-1 block text-sm font-medium" htmlFor="project-description">
              Description
            </label>
            <textarea
              id="project-description"
              disabled={!canManage}
              className="h-24 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:cursor-not-allowed"
              value={formState.description}
              onChange={handleFieldChange("description")}
            />
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Button type="submit" disabled={!canManage || isUpdating}>
            {isUpdating ? "Saving..." : "Save changes"}
          </Button>
          {error ? <span className="text-sm text-destructive">{error}</span> : null}
          {success ? <span className="text-sm text-green-600">{success}</span> : null}
        </div>
      </section>

      <section className="grid gap-4 rounded-lg border bg-card p-6 shadow-sm">
        <div>
          <h2 className="text-xl font-semibold">Linked context</h2>
          <p className="text-sm text-muted-foreground">
            Personas and requirements provide the context your team relies on.
          </p>
        </div>
        <div className="grid gap-2 text-sm">
          <p>
            <span className="font-medium">Personas:</span> {currentProject.personas.length}
          </p>
          <p>
            <span className="font-medium">Requirements:</span> {currentProject.requirementCounts.total}
          </p>
          {Object.entries(currentProject.requirementCounts.byType).length > 0 ? (
            <div>
              <span className="font-medium">By type:</span>
              <ul className="ml-4 list-disc">
                {Object.entries(currentProject.requirementCounts.byType).map(([type, count]) => (
                  <li key={type}>
                    {type}: {count}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
        <div className="grid gap-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Personas</span>
            <Link
              href={`/projects/${currentProject.id}/personas`}
              className="text-sm text-primary hover:underline"
            >
              Manage
            </Link>
          </div>
          {currentProject.personas.length === 0 ? (
            <p className="text-sm text-muted-foreground">No personas linked yet.</p>
          ) : (
            <ul className="grid gap-1 text-sm">
              {currentProject.personas.map((persona) => (
                <li key={persona.id} className="flex justify-between rounded-md border px-3 py-2">
                  <span>{persona.displayName}</span>
                  <span className="text-muted-foreground">{persona.role}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      <section className="grid gap-3 rounded-lg border border-destructive/40 bg-card p-6 shadow-sm">
        <div>
          <h2 className="text-xl font-semibold text-destructive">Danger zone</h2>
          <p className="text-sm text-muted-foreground">
            Deleting a project removes associated personas, requirements, and conversation history.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Button
            type="button"
            variant="destructive"
            disabled={!canManage || isDeleting}
            onClick={handleDelete}
          >
            {isDeleting ? "Deleting..." : "Delete project"}
          </Button>
          <Button asChild variant="outline">
            <Link href="/projects">Back to projects</Link>
          </Button>
        </div>
      </section>
    </form>
  );



}

