"use client";

import type { ChangeEvent, FormEvent } from "react";
import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";

import {
  PERSONA_ROLE_OPTIONS,
  type PersonaRole,
  type PersonaSummary,
  createPersona,
  deletePersona,
  updatePersona
} from "@/lib/api";

interface ProjectPersonasManagerProps {
  projectId: number;
  projectName: string;
  initialPersonas: PersonaSummary[];
  canManage: boolean;
}

interface PersonaFormState {
  displayName: string;
  role: PersonaRole;
}

const ROLE_LABELS: Record<PersonaRole, string> = {
  client: "Client",
  lead: "Lead",
  developer: "Developer",
  pm_agent: "PM Agent"
};

function toSummary(persona: PersonaSummary): PersonaSummary {
  return {
    id: persona.id,
    displayName: persona.displayName,
    role: persona.role
  };
}

export function ProjectPersonasManager({
  projectId,
  projectName,
  initialPersonas,
  canManage
}: ProjectPersonasManagerProps) {
  const [personas, setPersonas] = useState<PersonaSummary[]>(() => initialPersonas.map(toSummary));
  const [createState, setCreateState] = useState<PersonaFormState>({
    displayName: "",
    role: PERSONA_ROLE_OPTIONS[0]
  });
  const [editPersonaId, setEditPersonaId] = useState<string | null>(null);
  const [editState, setEditState] = useState<PersonaFormState>({
    displayName: "",
    role: PERSONA_ROLE_OPTIONS[0]
  });
  const [isCreating, setIsCreating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{ type: "error" | "success"; message: string } | null>(null);

  const hasPersonas = personas.length > 0;
  const personaCountLabel = useMemo(() => {
    return `${personas.length} persona${personas.length === 1 ? "" : "s"}`;
  }, [personas.length]);

  const resetFeedback = () => setFeedback(null);

  const handleCreateFieldChange = (field: keyof PersonaFormState) => (
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    resetFeedback();
    setCreateState((previous) => ({
      ...previous,
      [field]: event.target.value as PersonaRole | string
    }) as PersonaFormState);
  };

  const handleEditFieldChange = (field: keyof PersonaFormState) => (
    event: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    resetFeedback();
    setEditState((previous) => ({
      ...previous,
      [field]: event.target.value as PersonaRole | string
    }) as PersonaFormState);
  };

  const handleCreatePersona = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    resetFeedback();

    if (!canManage) {
      return;
    }

    const trimmedName = createState.displayName.trim();
    if (!trimmedName) {
      setFeedback({ type: "error", message: "Display name is required" });
      return;
    }

    setIsCreating(true);
    try {
      const created = await createPersona({
        projectId,
        role: createState.role,
        displayName: trimmedName
      });
      setPersonas((previous) => [...previous, toSummary(created)]);
      setCreateState({ displayName: "", role: createState.role });
      setFeedback({ type: "success", message: `Added persona "${created.displayName}".` });
    } catch (error) {
      setFeedback({
        type: "error",
        message: error instanceof Error ? error.message : "Failed to create persona"
      });
    } finally {
      setIsCreating(false);
    }
  };

  const handleStartEdit = (persona: PersonaSummary) => {
    resetFeedback();
    setEditPersonaId(persona.id);
    setEditState({ displayName: persona.displayName, role: persona.role });
  };

  const handleCancelEdit = () => {
    setEditPersonaId(null);
    setEditState({ displayName: "", role: PERSONA_ROLE_OPTIONS[0] });
  };

  const handleUpdatePersona = async (
    event: FormEvent<HTMLFormElement>,
    personaId: string
  ) => {
    event.preventDefault();
    resetFeedback();

    if (!canManage) {
      return;
    }

    const trimmedName = editState.displayName.trim();
    if (!trimmedName) {
      setFeedback({ type: "error", message: "Display name is required" });
      return;
    }

    setIsSaving(true);
    try {
      const updated = await updatePersona(personaId, {
        displayName: trimmedName,
        role: editState.role
      });
      setPersonas((previous) =>
        previous.map((persona) =>
          persona.id === personaId ? toSummary(updated) : persona
        )
      );
      setFeedback({ type: "success", message: `Updated persona "${updated.displayName}".` });
      setEditPersonaId(null);
      setEditState({ displayName: "", role: PERSONA_ROLE_OPTIONS[0] });
    } catch (error) {
      setFeedback({
        type: "error",
        message: error instanceof Error ? error.message : "Failed to update persona"
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeletePersona = async (personaId: string) => {
    resetFeedback();

    if (!canManage) {
      return;
    }

    const persona = personas.find((item) => item.id === personaId);
    const displayName = persona?.displayName ?? "this persona";
    const confirmed = typeof window === "undefined" ? true : window.confirm(`Delete "${displayName}"?`);
    if (!confirmed) {
      return;
    }

    setDeletingId(personaId);
    try {
      await deletePersona(personaId);
      setPersonas((previous) => previous.filter((item) => item.id !== personaId));
      if (editPersonaId === personaId) {
        handleCancelEdit();
      }
      setFeedback({ type: "success", message: `Removed persona "${displayName}".` });
    } catch (error) {
      setFeedback({
        type: "error",
        message: error instanceof Error ? error.message : "Failed to delete persona"
      });
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <section className="grid gap-6">
      <div className="rounded-lg border bg-card p-6 shadow-sm">
        <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="text-xl font-semibold">Persona roster</h2>
            <p className="text-sm text-muted-foreground">
              {personaCountLabel} linked to {projectName}.
            </p>
          </div>
          {!canManage ? (
            <p className="text-sm text-muted-foreground">
              You need lead or admin access to modify personas.
            </p>
          ) : null}
        </div>

        {feedback ? (
          <p
            className={
              feedback.type === "error" ? "mt-4 text-sm text-destructive" : "mt-4 text-sm text-green-600"
            }
          >
            {feedback.message}
          </p>
        ) : null}

        {canManage ? (
          <form className="mt-6 grid gap-4 md:grid-cols-[2fr_1fr_auto]" onSubmit={handleCreatePersona}>
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium" htmlFor="persona-display-name">
                Display name
              </label>
              <input
                id="persona-display-name"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Stakeholder name"
                value={createState.displayName}
                onChange={handleCreateFieldChange("displayName")}
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className="text-sm font-medium" htmlFor="persona-role">
                Role
              </label>
              <select
                id="persona-role"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
                value={createState.role}
                onChange={handleCreateFieldChange("role")}
              >
                {PERSONA_ROLE_OPTIONS.map((role) => (
                  <option key={role} value={role}>
                    {ROLE_LABELS[role]}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <Button type="submit" disabled={isCreating}>
                {isCreating ? "Adding..." : "Add persona"}
              </Button>
            </div>
          </form>
        ) : null}
      </div>

      <div className="rounded-lg border bg-card p-6 shadow-sm">
        <h3 className="text-lg font-semibold">Linked personas</h3>
        {!hasPersonas ? (
          <p className="mt-4 text-sm text-muted-foreground">No personas yet. Add one to capture discovery context.</p>
        ) : (
          <ul className="mt-4 grid gap-3">
            {personas.map((persona) => (
              <li key={persona.id} className="rounded-md border px-4 py-3">
                {editPersonaId === persona.id ? (
                  <form className="grid gap-3 md:grid-cols-[2fr_1fr_auto_auto]" onSubmit={(event) => handleUpdatePersona(event, persona.id)}>
                    <input
                      className="rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
                      value={editState.displayName}
                      onChange={handleEditFieldChange("displayName")}
                      disabled={isSaving}
                    />
                    <select
                      className="rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
                      value={editState.role}
                      onChange={handleEditFieldChange("role")}
                      disabled={isSaving}
                    >
                      {PERSONA_ROLE_OPTIONS.map((role) => (
                        <option key={role} value={role}>
                          {ROLE_LABELS[role]}
                        </option>
                      ))}
                    </select>
                    <Button type="submit" size="sm" disabled={isSaving}>
                      {isSaving ? "Saving..." : "Save"}
                    </Button>
                    <Button type="button" size="sm" variant="outline" onClick={handleCancelEdit} disabled={isSaving}>
                      Cancel
                    </Button>
                  </form>
                ) : (
                  <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                    <div>
                      <p className="text-sm font-medium">{persona.displayName}</p>
                      <p className="text-xs uppercase tracking-wide text-muted-foreground">{ROLE_LABELS[persona.role]}</p>
                    </div>
                    {canManage ? (
                      <div className="flex flex-wrap gap-2">
                        <Button size="sm" variant="outline" onClick={() => handleStartEdit(persona)}>
                          Edit
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleDeletePersona(persona.id)}
                          disabled={deletingId === persona.id}
                        >
                          {deletingId === persona.id ? "Removing..." : "Delete"}
                        </Button>
                      </div>
                    ) : null}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}