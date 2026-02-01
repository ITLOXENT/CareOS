"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";

import type {
  Conversation,
  Episode,
  EpisodeEvent,
  EvidenceBundle,
  EvidenceItem,
  FormTemplate,
  Message,
  Appointment,
  Task,
  WorkItem
} from "@careos/sdk";

import { apiClient } from "../../../lib/api";

type FormState = {
  symptoms: string;
  notes: string;
};

const TRANSITIONS: Record<string, string[]> = {
  new: ["triage"],
  triage: ["in_progress"],
  in_progress: ["waiting", "resolved"],
  waiting: ["in_progress"],
  resolved: ["closed"],
  closed: [],
  cancelled: []
};

export default function EpisodeDetailPage() {
  const params = useParams<{ id: string }>();
  const episodeId = Number(params.id);
  const [episode, setEpisode] = useState<Episode | null>(null);
  const [timeline, setTimeline] = useState<EpisodeEvent[]>([]);
  const [workItems, setWorkItems] = useState<WorkItem[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [evidenceItems, setEvidenceItems] = useState<EvidenceItem[]>([]);
  const [bundles, setBundles] = useState<EvidenceBundle[]>([]);
  const [evidenceKind, setEvidenceKind] = useState("");
  const [evidenceTitle, setEvidenceTitle] = useState("");
  const [evidenceTags, setEvidenceTags] = useState("");
  const [evidenceFile, setEvidenceFile] = useState<File | null>(null);
  const [linkEvidenceId, setLinkEvidenceId] = useState("");
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [messageBody, setMessageBody] = useState("");
  const [participantIds, setParticipantIds] = useState("");
  const [aiReviewStatus, setAiReviewStatus] = useState("");
  const [aiReviewSummary, setAiReviewSummary] = useState("");
  const [assignmentInputs, setAssignmentInputs] = useState<Record<number, string>>({});
  const [templates, setTemplates] = useState<FormTemplate[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState<number | null>(null);
  const [formState, setFormState] = useState<FormState>({ symptoms: "", notes: "" });
  const [responseId, setResponseId] = useState<number | null>(null);
  const [packId, setPackId] = useState<number | null>(null);
  const [status, setStatus] = useState("");
  const [currentRole, setCurrentRole] = useState<string | null>(null);

  const loadEpisode = async () => {
    try {
      const payload = await apiClient.getEpisode(episodeId);
      setEpisode(payload);
    } catch (error) {
      setStatus(String(error));
    }
  };

  const loadTimeline = async () => {
    try {
      const payload = await apiClient.getEpisodeTimeline(episodeId);
      setTimeline(payload.results);
    } catch (error) {
      setStatus(String(error));
    }
  };

  const loadWorkItems = async () => {
    try {
      const payload = await apiClient.listWorkItems({ episode_id: episodeId });
      setWorkItems(payload.results);
    } catch (error) {
      setStatus(String(error));
    }
  };

  const loadAppointments = async () => {
    try {
      const payload = await apiClient.listAppointments({ episode_id: episodeId });
      setAppointments(payload.results);
    } catch (error) {
      setStatus(String(error));
    }
  };

  const loadTasks = async () => {
    try {
      const payload = await apiClient.listTasks({ episode_id: episodeId });
      setTasks(payload.results);
    } catch (error) {
      setStatus(String(error));
    }
  };

  const loadEvidence = async () => {
    try {
      const payload = await apiClient.listEpisodeEvidence(episodeId);
      setEvidenceItems(payload.results);
    } catch (error) {
      setStatus(String(error));
    }
  };

  const loadBundles = async () => {
    try {
      const payload = await apiClient.listEpisodeBundles(episodeId);
      setBundles(payload.results);
    } catch (error) {
      setStatus(String(error));
    }
  };

  const loadConversations = async () => {
    try {
      const payload = await apiClient.listConversations({ episode_id: episodeId });
      setConversations(payload.results);
      if (payload.results.length > 0) {
        await loadConversationDetail(payload.results[0].id);
      }
    } catch (error) {
      setStatus(String(error));
    }
  };

  const loadConversationDetail = async (conversationId: number) => {
    try {
      const payload = await apiClient.getConversation(conversationId);
      setConversation(payload);
      setMessages(payload.messages);
    } catch (error) {
      setStatus(String(error));
    }
  };

  useEffect(() => {
    apiClient
      .listFormTemplates()
      .then((payload) => {
        setTemplates(payload.results);
        if (payload.results.length > 0) {
          setSelectedTemplateId(payload.results[0].id);
        }
      })
      .catch((error) => setStatus(String(error)));
  }, []);

  useEffect(() => {
    if (!episodeId) {
      return;
    }
    apiClient
      .me()
      .then((payload) => setCurrentRole(payload.role))
      .catch(() => setCurrentRole(null));
    loadEpisode();
    loadTimeline();
    loadWorkItems();
    loadAppointments();
    loadTasks();
    loadEvidence();
    loadBundles();
    loadConversations();
  }, [episodeId]);

  const selectedTemplate = useMemo(
    () => templates.find((template) => template.id === selectedTemplateId) ?? null,
    [templates, selectedTemplateId]
  );

  const handleCreateResponse = async () => {
    if (!episodeId || !selectedTemplateId) {
      setStatus("Missing episode or template selection.");
      return;
    }
    setStatus("Submitting response...");
    try {
      const response = await apiClient.createFormResponse({
        episode_id: episodeId,
        template_id: selectedTemplateId,
        data: { symptoms: formState.symptoms, notes: formState.notes }
      });
      setResponseId(response.id);
      if (!response.validated) {
        setStatus(`Validation issues: ${response.validation_errors.join(", ")}`);
        return;
      }
      setStatus("Response saved.");
      await loadTimeline();
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleSign = async () => {
    if (!responseId) {
      setStatus("Create a response first.");
      return;
    }
    setStatus("Signing...");
    try {
      await apiClient.signFormResponse(responseId);
      setStatus("Signed.");
      await loadTimeline();
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleGeneratePack = async () => {
    setStatus("Generating evidence pack...");
    try {
      const result = await apiClient.generateEvidencePack(episodeId);
      setPackId(result.id);
      setStatus("Evidence pack ready.");
      await loadTimeline();
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleGenerateBundle = async () => {
    setStatus("Generating compliance bundle...");
    try {
      await apiClient.generateEpisodeBundle(episodeId);
      setStatus("Compliance bundle ready.");
      await loadBundles();
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleBundleDownload = async (bundleId: number) => {
    setStatus("Downloading compliance bundle...");
    try {
      const blob = await apiClient.downloadEpisodeBundle(bundleId);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `compliance-bundle-${bundleId}.zip`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleDownload = async () => {
    if (!packId) {
      return;
    }
    setStatus("Downloading...");
    try {
      const blob = await apiClient.downloadEvidencePack(packId);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `evidence-pack-${packId}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setStatus("Download started.");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleTransition = async (nextState: string) => {
    setStatus(`Transitioning to ${nextState}...`);
    try {
      await apiClient.transitionEpisode(episodeId, { to_state: nextState });
      await loadEpisode();
      await loadTimeline();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleAssign = async (itemId: number) => {
    const assignedToValue = assignmentInputs[itemId];
    if (!assignedToValue) {
      setStatus("Enter a user id to assign.");
      return;
    }
    setStatus("Assigning work item...");
    try {
      await apiClient.assignWorkItem(itemId, Number(assignedToValue));
      await loadWorkItems();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleComplete = async (itemId: number) => {
    setStatus("Completing work item...");
    try {
      await apiClient.completeWorkItem(itemId);
      await loadWorkItems();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleEvidenceUpload = async () => {
    if (!evidenceFile) {
      setStatus("Select a file to upload.");
      return;
    }
    if (!evidenceKind.trim()) {
      setStatus("Evidence kind is required.");
      return;
    }
    setStatus("Uploading evidence...");
    const formData = new FormData();
    formData.append("file", evidenceFile);
    formData.append("kind", evidenceKind.trim());
    if (evidenceTitle.trim()) {
      formData.append("title", evidenceTitle.trim());
    }
    if (evidenceTags.trim()) {
      formData.append("tags", evidenceTags.trim());
    }
    try {
      await apiClient.createEpisodeEvidence(episodeId, formData);
      setEvidenceKind("");
      setEvidenceTitle("");
      setEvidenceTags("");
      setEvidenceFile(null);
      await loadEvidence();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleEvidenceLink = async () => {
    if (!linkEvidenceId.trim()) {
      setStatus("Provide an evidence id to link.");
      return;
    }
    setStatus("Linking evidence...");
    try {
      await apiClient.linkEpisodeEvidence(episodeId, Number(linkEvidenceId));
      setLinkEvidenceId("");
      await loadEvidence();
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleEvidenceDownload = async (evidenceId: number, fileName: string) => {
    setStatus("Downloading evidence...");
    try {
      const blob = await apiClient.downloadEvidence(evidenceId);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = fileName || `evidence-${evidenceId}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleCreateConversation = async () => {
    const ids = participantIds
      .split(",")
      .map((value) => Number(value.trim()))
      .filter((value) => Number.isFinite(value));
    setStatus("Creating conversation...");
    try {
      const created = await apiClient.createConversation({
        episode_id: episodeId,
        participants: ids
      });
      setParticipantIds("");
      await loadConversations();
      await loadConversationDetail(created.id);
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleSendMessage = async () => {
    if (!conversation) {
      setStatus("Create or select a conversation first.");
      return;
    }
    if (!messageBody.trim()) {
      setStatus("Message body is required.");
      return;
    }
    setStatus("Sending message...");
    try {
      await apiClient.sendMessage(conversation.id, { body: messageBody.trim() });
      setMessageBody("");
      await loadConversationDetail(conversation.id);
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleMarkRead = async (messageId: number) => {
    try {
      await apiClient.markMessageRead(messageId);
      if (conversation) {
        await loadConversationDetail(conversation.id);
      }
    } catch (error) {
      setStatus(String(error));
    }
  };

  const handleGenerateSummary = async () => {
    if (!episode) {
      setStatus("Episode not loaded.");
      return;
    }
    setStatus("Generating AI summary...");
    try {
      const review = await apiClient.createAiReview({
        input_type: "episode.summary",
        payload: {
          episode_id: episode.id,
          text: episode.description || episode.title
        }
      });
      setAiReviewStatus(review.status);
      const detail = await apiClient.getAiReview(review.id);
      setAiReviewStatus(detail.status);
      if (detail.output?.summary) {
        setAiReviewSummary(String(detail.output.summary));
      }
      setStatus("");
    } catch (error) {
      setStatus(String(error));
    }
  };

  const transitions = useMemo(() => {
    if (!episode) {
      return [];
    }
    const base = TRANSITIONS[episode.status] ?? [];
    if (currentRole === "ADMIN") {
      return [...base, "cancelled"];
    }
    return base;
  }, [episode, currentRole]);

  return (
    <section className="panel">
      <h2>Episode {episodeId}</h2>
      {episode ? (
        <p className="status">
          Status: {episode.status} · Assigned {episode.assigned_to ?? "unassigned"}
        </p>
      ) : null}

      <div style={{ marginTop: "12px" }}>
        <h3>Transitions</h3>
        <div className="row" style={{ flexWrap: "wrap" }}>
          {transitions.length > 0 ? (
            transitions.map((nextState) => (
              <button
                key={nextState}
                className="button secondary"
                type="button"
                onClick={() => handleTransition(nextState)}
              >
                {nextState}
              </button>
            ))
          ) : (
            <p className="status">No transitions available.</p>
          )}
        </div>
      </div>

      <div style={{ marginTop: "16px" }}>
        <h3>Timeline</h3>
        {timeline.map((event) => (
          <div key={event.id} className="row" style={{ marginBottom: "8px" }}>
            <div>
              <div>{event.event_type}</div>
              <div className="status">
                {event.from_status || event.from_state
                  ? `${event.from_status ?? event.from_state} → ${event.to_status ?? event.to_state}`
                  : event.to_status ?? event.to_state}{" "}
                · {event.created_at}
              </div>
            </div>
          </div>
        ))}
        {timeline.length === 0 ? <p className="status">No events yet.</p> : null}
      </div>

      <div style={{ marginTop: "16px" }}>
        <h3>Work items</h3>
        {workItems.map((item) => (
          <div key={item.id} className="row" style={{ marginBottom: "12px" }}>
            <div style={{ minWidth: "180px" }}>
              <div>{item.kind}</div>
              <div className="status">{item.status}</div>
            </div>
            <input
              className="input"
              placeholder="Assign to (user id)"
              value={assignmentInputs[item.id] ?? ""}
              onChange={(event) =>
                setAssignmentInputs((prev) => ({ ...prev, [item.id]: event.target.value }))
              }
            />
            <button className="button secondary" type="button" onClick={() => handleAssign(item.id)}>
              Assign
            </button>
            <button className="button secondary" type="button" onClick={() => handleComplete(item.id)}>
              Complete
            </button>
          </div>
        ))}
        {workItems.length === 0 ? <p className="status">No work items yet.</p> : null}
      </div>

      <div style={{ marginTop: "16px" }}>
        <h3>Appointments</h3>
        {appointments.map((appointment) => (
          <div key={appointment.id} className="row" style={{ marginBottom: "8px" }}>
            <div>
              <div>
                {appointment.status} · {appointment.scheduled_at}
              </div>
              <div className="status">
                {appointment.location || "No location"} · {appointment.duration_minutes} min
              </div>
            </div>
          </div>
        ))}
        {appointments.length === 0 ? (
          <p className="status">No appointments linked.</p>
        ) : null}
      </div>

      <div style={{ marginTop: "16px" }}>
        <h3>Tasks</h3>
        {tasks.map((task) => (
          <div key={task.id} className="row" style={{ marginBottom: "8px" }}>
            <div>
              <div>
                {task.title} · {task.status}
              </div>
              <div className="status">
                priority {task.priority} · due {task.due_at ?? "n/a"}
              </div>
            </div>
          </div>
        ))}
        {tasks.length === 0 ? <p className="status">No tasks linked.</p> : null}
      </div>

      <div style={{ marginTop: "16px" }}>
        <h3>Evidence</h3>
        {evidenceItems.map((item) => (
          <div key={item.id} className="row" style={{ marginBottom: "8px" }}>
            <div>
              <div>{item.title}</div>
              <div className="status">
                {item.kind} · tags {(item.tags || []).join(", ") || "none"}
              </div>
            </div>
            <button
              className="button secondary"
              type="button"
              onClick={() => handleEvidenceDownload(item.id, item.file_name)}
            >
              Download
            </button>
          </div>
        ))}
        {evidenceItems.length === 0 ? <p className="status">No evidence linked.</p> : null}
        <div className="row" style={{ marginTop: "12px", flexWrap: "wrap" }}>
          <input
            className="input"
            placeholder="Evidence id to link"
            value={linkEvidenceId}
            onChange={(event) => setLinkEvidenceId(event.target.value)}
          />
          <button className="button secondary" type="button" onClick={handleEvidenceLink}>
            Link evidence
          </button>
        </div>
        <div className="form" style={{ marginTop: "12px" }}>
          <h4>Upload evidence</h4>
          <input
            className="input"
            placeholder="Title (optional)"
            value={evidenceTitle}
            onChange={(event) => setEvidenceTitle(event.target.value)}
          />
          <input
            className="input"
            placeholder="Kind"
            value={evidenceKind}
            onChange={(event) => setEvidenceKind(event.target.value)}
          />
          <input
            className="input"
            placeholder="Tags (comma separated)"
            value={evidenceTags}
            onChange={(event) => setEvidenceTags(event.target.value)}
          />
          <input
            className="input"
            type="file"
            onChange={(event) => setEvidenceFile(event.target.files?.[0] ?? null)}
          />
          <button className="button" type="button" onClick={handleEvidenceUpload}>
            Upload evidence
          </button>
        </div>
      </div>

      <div style={{ marginTop: "16px" }}>
        <h3>Compliance</h3>
        <button className="button secondary" type="button" onClick={handleGenerateBundle}>
          Generate bundle
        </button>
        <div style={{ marginTop: "12px" }}>
          {bundles.map((bundle) => (
            <div key={bundle.id} className="row" style={{ marginBottom: "8px" }}>
              <div>
                <div>Bundle {bundle.id}</div>
                <div className="status">{bundle.created_at}</div>
              </div>
              <button
                className="button secondary"
                type="button"
                onClick={() => handleBundleDownload(bundle.id)}
              >
                Download
              </button>
            </div>
          ))}
          {bundles.length === 0 ? <p className="status">No bundles generated yet.</p> : null}
        </div>
      </div>

      <div style={{ marginTop: "16px" }}>
        <h3>Messages</h3>
        <div className="row" style={{ flexWrap: "wrap" }}>
          {conversations.map((item) => (
            <button
              key={item.id}
              className="button secondary"
              type="button"
              onClick={() => loadConversationDetail(item.id)}
            >
              Conversation {item.id}
            </button>
          ))}
          {conversations.length === 0 ? (
            <span className="status">No conversations yet.</span>
          ) : null}
        </div>

        <div className="form" style={{ marginTop: "12px" }}>
          <h4>Create conversation</h4>
          <input
            className="input"
            placeholder="Participant user ids (comma-separated)"
            value={participantIds}
            onChange={(event) => setParticipantIds(event.target.value)}
          />
          <button className="button secondary" type="button" onClick={handleCreateConversation}>
            Create conversation
          </button>
        </div>

        {conversation ? (
          <div style={{ marginTop: "12px" }}>
            <h4>Conversation {conversation.id}</h4>
            {messages.map((message) => (
              <div key={message.id} className="row" style={{ marginBottom: "8px" }}>
                <div>
                  <div>{message.body}</div>
                  <div className="status">
                    sender {message.sender_id ?? "n/a"} · {message.created_at}
                  </div>
                </div>
                <button
                  className="button secondary"
                  type="button"
                  onClick={() => handleMarkRead(message.id)}
                >
                  Mark read
                </button>
              </div>
            ))}
            {messages.length === 0 ? <p className="status">No messages yet.</p> : null}
            <div className="form" style={{ marginTop: "12px" }}>
              <h4>Send message</h4>
              <textarea
                className="input"
                rows={3}
                placeholder="Message"
                value={messageBody}
                onChange={(event) => setMessageBody(event.target.value)}
              />
              <button className="button" type="button" onClick={handleSendMessage}>
                Send message
              </button>
            </div>
          </div>
        ) : null}
      </div>

      <div style={{ marginTop: "16px" }}>
        <h3>AI Review</h3>
        <button className="button secondary" type="button" onClick={handleGenerateSummary}>
          Generate summary
        </button>
        {aiReviewStatus ? <p className="status">Status: {aiReviewStatus}</p> : null}
        {aiReviewSummary ? <p className="status">Summary: {aiReviewSummary}</p> : null}
      </div>

      <div className="form" style={{ marginTop: "24px" }}>
        <h3>Intake form</h3>
        <label className="status">Template</label>
        <select
          className="input"
          value={selectedTemplateId ?? ""}
          onChange={(event) => setSelectedTemplateId(Number(event.target.value))}
        >
          <option value="" disabled>
            Select template
          </option>
          {templates.map((template) => (
            <option key={template.id} value={template.id}>
              {template.name} (v{template.version})
            </option>
          ))}
        </select>

        <label className="status">Symptoms</label>
        <textarea
          className="input"
          rows={3}
          value={formState.symptoms}
          onChange={(event) => setFormState({ ...formState, symptoms: event.target.value })}
        />

        <label className="status">Notes</label>
        <textarea
          className="input"
          rows={4}
          value={formState.notes}
          onChange={(event) => setFormState({ ...formState, notes: event.target.value })}
        />

        <div className="row">
          <button className="button" type="button" onClick={handleCreateResponse}>
            Save response
          </button>
          <button className="button secondary" type="button" onClick={handleSign}>
            Sign
          </button>
          <button className="button secondary" type="button" onClick={handleGeneratePack}>
            Generate evidence pack
          </button>
          <button className="button secondary" type="button" onClick={handleDownload}>
            Download PDF
          </button>
        </div>
        {selectedTemplate ? (
          <p className="status">Active template: {selectedTemplate.name}</p>
        ) : null}
      </div>
      {status ? <p className="status">{status}</p> : null}
    </section>
  );
}
