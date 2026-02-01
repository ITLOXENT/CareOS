import {
  createAdminClient,
  createAiReviewClient,
  createAiClient,
  createAppointmentsClient,
  createBillingClient,
  createComplianceClient,
  createClient,
  createEvidenceClient,
  createEpisodesClient,
  createExportsClient,
  createFormsClient,
  createIntegrationsClient,
  createInteropClient,
  createMessagesClient,
  createNotificationsClient,
  createPatientsClient,
  createTasksClient
} from "@careos/sdk";
import type { AuditEventList, MeResponse, OrgResponse } from "@careos/types";

const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const client = createClient({ baseUrl });
const formsClient = createFormsClient({ baseUrl });
const aiClient = createAiClient({ baseUrl });
const adminClient = createAdminClient({ baseUrl });
const aiReviewClient = createAiReviewClient({ baseUrl });
const billingClient = createBillingClient({ baseUrl });
const appointmentsClient = createAppointmentsClient({ baseUrl });
const evidenceClient = createEvidenceClient({ baseUrl });
const complianceClient = createComplianceClient({ baseUrl });
const exportsClient = createExportsClient({ baseUrl });
const integrationsClient = createIntegrationsClient({ baseUrl });
const interopClient = createInteropClient({ baseUrl });
const episodesClient = createEpisodesClient({ baseUrl });
const patientsClient = createPatientsClient({ baseUrl });
const notificationsClient = createNotificationsClient({ baseUrl });
const messagesClient = createMessagesClient({ baseUrl });
const tasksClient = createTasksClient({ baseUrl });

export const apiClient = {
  me: (): Promise<MeResponse> => client.get_me(),
  getCurrentOrg: (): Promise<OrgResponse> => client.get_orgs_current(),
  listAuditEvents: (): Promise<AuditEventList> => client.get_audit_events(),
  listFormTemplates: () => formsClient.listTemplates(),
  createFormResponse: formsClient.createResponse,
  signFormResponse: formsClient.signResponse,
  generateEvidencePack: formsClient.generateEvidencePack,
  downloadEvidencePack: formsClient.downloadEvidencePack,
  listAiArtifacts: (status?: string) => aiClient.listArtifacts(status),
  approveAiArtifact: (artifactId: number) => aiClient.approve(artifactId),
  rejectAiArtifact: (artifactId: number, reason: string) =>
    aiClient.reject(artifactId, reason),
  listInteropMessages: () => interopClient.listMessages(),
  processInteropOutbox: () => interopClient.processOutbox(),
  listEpisodes: episodesClient.listEpisodes,
  createEpisode: episodesClient.createEpisode,
  getEpisode: episodesClient.getEpisode,
  transitionEpisode: episodesClient.transitionEpisode,
  getEpisodeTimeline: episodesClient.getEpisodeTimeline,
  listWorkItems: episodesClient.listWorkItems,
  assignWorkItem: episodesClient.assignWorkItem,
  completeWorkItem: episodesClient.completeWorkItem,
  listPatients: patientsClient.listPatients,
  createPatient: patientsClient.createPatient,
  getPatient: patientsClient.getPatient,
  mergePatient: patientsClient.mergePatient,
  listEvidence: evidenceClient.listEvidence,
  createEvidence: evidenceClient.createEvidence,
  getEvidence: evidenceClient.getEvidence,
  downloadEvidence: evidenceClient.downloadEvidence,
  listEpisodeEvidence: evidenceClient.listEpisodeEvidence,
  createEpisodeEvidence: evidenceClient.createEpisodeEvidence,
  linkEpisodeEvidence: evidenceClient.linkEpisodeEvidence,
  linkEvidence: evidenceClient.linkEvidence,
  tagEvidence: evidenceClient.tagEvidence,
  listEpisodeBundles: complianceClient.listEpisodeBundles,
  generateEpisodeBundle: complianceClient.generateEpisodeBundle,
  downloadEpisodeBundle: complianceClient.downloadEpisodeBundle,
  listExports: exportsClient.listExports,
  requestExport: exportsClient.requestExport,
  getExport: exportsClient.getExport,
  downloadExport: exportsClient.downloadExport,
  listNotifications: notificationsClient.listNotifications,
  markNotificationRead: notificationsClient.markRead,
  getOrgProfile: adminClient.getOrgProfile,
  updateOrgProfile: adminClient.updateOrgProfile,
  listOrgMembers: adminClient.listMembers,
  changeOrgMemberRole: adminClient.changeMemberRole,
  deactivateOrgMember: adminClient.deactivateMember,
  listOrgInvites: adminClient.listInvites,
  createOrgInvite: adminClient.createInvite,
  listConversations: messagesClient.listConversations,
  createConversation: messagesClient.createConversation,
  getConversation: messagesClient.getConversation,
  sendMessage: messagesClient.sendMessage,
  markMessageRead: messagesClient.markMessageRead,
  listBillingPlans: billingClient.listPlans,
  createBillingCheckout: billingClient.createCheckoutSession,
  getBillingSubscription: billingClient.getSubscription,
  listIntegrations: integrationsClient.listIntegrations,
  connectIntegration: integrationsClient.connect,
  testIntegration: integrationsClient.test,
  disconnectIntegration: integrationsClient.disconnect,
  listIntegrationApiKeys: integrationsClient.listApiKeys,
  createIntegrationApiKey: integrationsClient.createApiKey,
  revokeIntegrationApiKey: integrationsClient.revokeApiKey,
  listAiReviews: aiReviewClient.list,
  createAiReview: aiReviewClient.create,
  getAiReview: aiReviewClient.get,
  listAiReviewItems: aiReviewClient.listItems,
  decideAiReviewItem: aiReviewClient.decideItem,
  listAppointments: appointmentsClient.listAppointments,
  createAppointment: appointmentsClient.createAppointment,
  transitionAppointment: appointmentsClient.transitionAppointment,
  listTasks: tasksClient.listTasks,
  createTask: tasksClient.createTask,
  assignTask: tasksClient.assignTask,
  completeTask: tasksClient.completeTask,
};
