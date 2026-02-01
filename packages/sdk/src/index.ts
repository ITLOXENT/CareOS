export { createClient } from "./generated";
export type { ClientOptions } from "./generated";
export { createFormsClient } from "./forms";
export type { EvidencePack, FormResponse, FormTemplate, FormsClientOptions } from "./forms";
export { createAiClient } from "./ai";
export type { AiArtifact, AiClientOptions, AiListResponse } from "./ai";
export { createAppointmentsClient } from "./appointments";
export type {
  Appointment,
  AppointmentListResponse,
  AppointmentsClientOptions
} from "./appointments";
export { createAiReviewClient } from "./ai_review";
export type {
  AiReviewClientOptions,
  AiReviewItem,
  AiReviewItemListResponse,
  AiReviewListResponse,
  AiReviewRequest
} from "./ai_review";
export { createInteropClient } from "./interop";
export type {
  InteropClientOptions,
  InteropListResponse,
  InteropMessage,
  InteropStatusEvent,
} from "./interop";
export { createEpisodesClient } from "./episodes";
export type {
  Episode,
  EpisodeEvent,
  EpisodeListResponse,
  EpisodeTimelineResponse,
  EpisodesClientOptions,
  WorkItem,
  WorkItemListResponse,
} from "./episodes";
export { createPatientsClient } from "./patients";
export type {
  CareCircleMember,
  Patient,
  PatientAddress,
  PatientContactMethod,
  PatientIdentifier,
  PatientConsent,
  PatientListResponse,
  PatientsClientOptions
} from "./patients";
export { createEvidenceClient } from "./evidence";
export type { EvidenceClientOptions, EvidenceItem, EvidenceListResponse } from "./evidence";
export { createExportsClient } from "./exports";
export type {
  ExportJob,
  ExportJobListResponse,
  ExportJobRequest,
  ExportsClientOptions
} from "./exports";
export { createNotificationsClient } from "./notifications";
export type {
  Notification,
  NotificationListResponse,
  NotificationsClientOptions,
} from "./notifications";
export { createAdminClient } from "./admin";
export type {
  AdminClientOptions,
  OrgInvite,
  OrgInviteListResponse,
  OrgMember,
  OrgMemberListResponse,
} from "./admin";
export { createPortalClient } from "./portal";
export type {
  PortalAcceptInviteRequest,
  PortalAuthResponse,
  PortalCareCircleMember,
  PortalConsent,
  PortalEpisode,
  PortalEpisodeDetail,
  PortalEpisodeEvent,
  PortalEpisodeListResponse,
  PortalLoginRequest,
  PortalMeResponse,
  PortalNotification,
  PortalNotificationListResponse,
  PortalClientOptions,
} from "./portal";
export { createMessagesClient } from "./messages";
export type {
  Conversation,
  ConversationDetail,
  ConversationListResponse,
  ConversationParticipant,
  Message,
  MessagesClientOptions,
} from "./messages";
export { createBillingClient } from "./billing";
export type {
  BillingClientOptions,
  BillingPlan,
  BillingPlanListResponse,
  BillingSubscription,
} from "./billing";
export { createComplianceClient } from "./compliance";
export type {
  ComplianceClientOptions,
  EvidenceBundle,
  EvidenceBundleListResponse,
  ReportJob,
  ReportJobListResponse,
  SubmissionRecord,
  SubmissionRecordListResponse,
} from "./compliance";
export { createPrivacyClient } from "./privacy";
export type {
  ConsentRecord,
  ConsentRecordListResponse,
  DsarExport,
  DsarExportListResponse,
  PrivacyClientOptions,
} from "./privacy";
export { createIntegrationsClient } from "./integrations";
export type {
  Integration,
  IntegrationApiKey,
  IntegrationApiKeyCreateResponse,
  IntegrationApiKeyListResponse,
  IntegrationListResponse,
  IntegrationsClientOptions,
} from "./integrations";
export { createTasksClient } from "./tasks";
export type { Task, TaskListResponse, TasksClientOptions } from "./tasks";
