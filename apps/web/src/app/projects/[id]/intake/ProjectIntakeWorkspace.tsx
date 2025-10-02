"use client";

import type { ChangeEvent, FormEvent } from "react";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import {
  extractRequirements,
  type PersonaSummary,
  type Requirement
} from "@/lib/api";

interface ProjectIntakeWorkspaceProps {
  projectId: number;
  projectName: string;
  personas: PersonaSummary[];
  initialRequirements: Requirement[];
  canExtract: boolean;
}

interface ConversationMessage {
  id: string;
  sender: "persona" | "system";
  text: string;
  personaId?: string;
  createdAt: string;
}

const createMessageId = () => {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

export function ProjectIntakeWorkspace({
  projectId,
  projectName,
  personas,
  initialRequirements,
  canExtract
}: ProjectIntakeWorkspaceProps) {
  const [selectedPersonaId, setSelectedPersonaId] = useState<string>(personas[0]?.id ?? "");
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [requirements, setRequirements] = useState<Requirement[]>(() => [...initialRequirements]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const personaById = useMemo(() => {
    return new Map(personas.map((persona) => [persona.id, persona]));
  }, [personas]);

  useEffect(() => {
    if (!selectedPersonaId && personas.length > 0) {
      setSelectedPersonaId(personas[0].id);
      return;
    }
    if (selectedPersonaId && !personaById.has(selectedPersonaId) && personas.length > 0) {
      setSelectedPersonaId(personas[0].id);
    }
  }, [personas, personaById, selectedPersonaId]);

  const sortedRequirements = useMemo(() => {
    return [...requirements].sort(
      (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  }, [requirements]);

  const handlePersonaChange = (event: ChangeEvent<HTMLSelectElement>) => {
    setSelectedPersonaId(event.target.value);
    setMessages([]);
  };

  const handleMessageChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(event.target.value);
  };

  const appendMessage = (entry: ConversationMessage) => {
    setMessages((previous) => [...previous, entry]);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (!canExtract || !selectedPersonaId) {
      return;
    }

    const trimmed = message.trim();
    if (!trimmed) {
      setError("Enter a message to run extraction");
      return;
    }

    const persona = personaById.get(selectedPersonaId);
    const personaLabel = persona ? `${persona.displayName} (${persona.role})` : "Persona";

    const personaMessage: ConversationMessage = {
      id: createMessageId(),
      sender: "persona",
      personaId: selectedPersonaId,
      text: trimmed,
      createdAt: new Date().toISOString()
    };
    appendMessage(personaMessage);
    setMessage("");
    setIsSubmitting(true);

    try {
      const extracted = await extractRequirements({
        projectId,
        personaId: selectedPersonaId,
        text: trimmed
      });

      setRequirements((previous) => {
        const map = new Map(previous.map((item) => [item.id, item]));
        extracted.forEach((item) => {
          map.set(item.id, item);
        });
        return Array.from(map.values());
      });

      const summary = extracted.length === 1
        ? "Created 1 requirement from this message."
        : `Created ${extracted.length} requirements from this message.`;

      appendMessage({
        id: createMessageId(),
        sender: "system",
        text: `${summary} ${personaLabel} provided the context.`,
        createdAt: new Date().toISOString()
      });
    } catch (submitError) {
      const messageText = submitError instanceof Error ? submitError.message : "Failed to extract requirements";
      setError(messageText);
      appendMessage({
        id: createMessageId(),
        sender: "system",
        text: `Extraction failed: ${messageText}`,
        createdAt: new Date().toISOString()
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const canSend = canExtract && personas.length > 0;
  const selectedPersona = selectedPersonaId ? personaById.get(selectedPersonaId) ?? null : null;

  return (
    <div className="grid gap-6 md:grid-cols-[2fr_1fr]">
      <section className="grid gap-4 rounded-lg border bg-card p-6 shadow-sm">
        <header className="flex flex-col gap-2">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between md:gap-4">
            <div>
              <h2 className="text-2xl font-semibold">Intake console</h2>
              <p className="text-sm text-muted-foreground">
                Send a message as a persona to capture structured requirements.
              </p>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <label className="font-medium" htmlFor="persona-select">
                Persona
              </label>
              <select
                id="persona-select"
                className="min-w-[180px] rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
                value={selectedPersonaId}
                onChange={handlePersonaChange}
                disabled={!canExtract || personas.length === 0}
              >
                {personas.map((persona) => (
                  <option key={persona.id} value={persona.id}>
                    {persona.displayName} ({persona.role})
                  </option>
                ))}
              </select>
            </div>
          </div>
          {selectedPersona ? (
            <p className="text-xs uppercase tracking-wide text-muted-foreground">
              {selectedPersona.displayName} · Role: {selectedPersona.role}
            </p>
          ) : (
            <p className="text-xs text-muted-foreground">
              Add a persona to enable intake.
            </p>
          )}
        </header>

        <div className="flex h-72 flex-col gap-3 overflow-y-auto rounded-md border border-dashed border-muted-foreground/30 p-4">
          {messages.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No conversation yet. Send a message to start extracting requirements for {projectName}.
            </p>
          ) : (
            messages.map((entry) => (
              <div
                key={entry.id}
                className={
                  entry.sender === "persona"
                    ? "self-start rounded-lg bg-primary/10 px-3 py-2 text-sm"
                    : "self-end rounded-lg bg-muted px-3 py-2 text-sm"
                }
              >
                <p className="whitespace-pre-line leading-relaxed">{entry.text}</p>
                <span className="mt-1 block text-xs text-muted-foreground">
                  {new Date(entry.createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  {entry.sender === "persona" ? " · Persona" : " · System"}
                </span>
              </div>
            ))
          )}
        </div>

        {error ? <p className="text-sm text-destructive">{error}</p> : null}

        <form className="grid gap-3" onSubmit={handleSubmit}>
          <label className="text-sm font-medium" htmlFor="intake-message">
            Message
          </label>
          <textarea
            id="intake-message"
            className="h-28 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Share discovery notes, feature ideas, or issues..."
            value={message}
            onChange={handleMessageChange}
            disabled={!canSend || isSubmitting}
          />
          <div className="flex items-center justify-end gap-3">
            <Button type="submit" disabled={!canSend || isSubmitting}>
              {isSubmitting ? "Extracting..." : "Send to extractor"}
            </Button>
          </div>
        </form>
      </section>

      <aside className="grid gap-4 rounded-lg border bg-card p-6 shadow-sm">
        <div>
          <h3 className="text-lg font-semibold">Extracted requirements</h3>
          <p className="text-sm text-muted-foreground">
            Automatically generated when personas contribute discovery notes.
          </p>
        </div>
        {sortedRequirements.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Requirements will appear here after extraction runs.
          </p>
        ) : (
          <ul className="grid gap-3 text-sm">
            {sortedRequirements.map((requirement) => {
              const persona = personaById.get(requirement.personaId);
              return (
                <li key={requirement.id} className="rounded-md border px-3 py-2">
                  <p className="font-medium leading-snug">{requirement.text}</p>
                  <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                    <span className="rounded-full bg-muted px-2 py-0.5 uppercase tracking-wide">
                      {requirement.type}
                    </span>
                    <span>
                      Persona role: {persona ? persona.role : "unknown"}
                    </span>
                    <span>
                      {new Date(requirement.createdAt).toLocaleDateString()} {new Date(requirement.createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </aside>
    </div>
  );
}
