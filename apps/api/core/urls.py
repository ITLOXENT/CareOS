from django.conf import settings
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import admin as admin_views
from .views import ai as ai_views
from .views import ai_review as ai_review_views
from .views import audit as audit_views
from .views import auth as auth_views
from .views import appointments as appointment_views
from .views import episodes as episode_views
from .views import evidence_items as evidence_item_views
from .views import evidence_packs as evidence_pack_views
from .views import forms as form_views
from .views import health as health_views
from .views import inbox as inbox_views
from .views import integrations as integration_views
from .views import me as me_views
from .views import messaging as messaging_views
from .views import notifications as notification_views
from .views import observability as observability_views
from .views import compliance as compliance_views
from .views import orgs as org_views
from .views import patients as patient_views
from .views import portal as portal_views
from .views import privacy as privacy_views
from .views import tasks as task_views
from .views import interop as interop_views


urlpatterns = [
    path("health/", health_views.health),
    path("healthz/", health_views.healthz),
    path("readyz/", health_views.readyz),
    path("me/", me_views.me),
    path("orgs/current/", csrf_exempt(me_views.current_org)),
    path("orgs/members/", org_views.org_members_list),
    path("orgs/invites/", csrf_exempt(org_views.org_invites)),
    path(
        "orgs/members/<int:member_id>/role/",
        csrf_exempt(org_views.org_member_change_role),
    ),
    path(
        "orgs/members/<int:member_id>/deactivate/",
        csrf_exempt(org_views.org_member_deactivate),
    ),
    path("audit-events/", audit_views.audit_events),
    path("billing/plans/", admin_views.billing_plans),
    path("billing/checkout-session/", csrf_exempt(admin_views.billing_checkout_session)),
    path("billing/subscription/", admin_views.billing_subscription),
    path("billing/webhook/", csrf_exempt(admin_views.billing_webhook)),
    path("integrations/", integration_views.integrations_list),
    path(
        "integrations/<str:provider>/connect/",
        csrf_exempt(integration_views.integrations_connect),
    ),
    path(
        "integrations/<str:provider>/test/",
        csrf_exempt(integration_views.integrations_test),
    ),
    path(
        "integrations/<str:provider>/disconnect/",
        csrf_exempt(integration_views.integrations_disconnect),
    ),
    path("integrations/api-keys/", csrf_exempt(integration_views.integration_api_keys)),
    path(
        "integrations/api-keys/<int:key_id>/revoke/",
        csrf_exempt(integration_views.integration_api_key_revoke),
    ),
    path("notifications/", notification_views.notifications_list),
    path(
        "notifications/<int:notification_id>/read/",
        csrf_exempt(notification_views.notification_mark_read),
    ),
    path("exports/", csrf_exempt(admin_views.exports_list)),
    path("exports/<int:export_id>/", admin_views.export_detail),
    path("exports/<int:export_id>/download/", admin_views.export_download),
    path("portal/auth/accept-invite/", csrf_exempt(portal_views.portal_accept_invite)),
    path("portal/auth/login/", csrf_exempt(portal_views.portal_login)),
    path("portal/me/", portal_views.portal_me),
    path("portal/episodes/", portal_views.portal_episodes),
    path("portal/episodes/<int:episode_id>/", portal_views.portal_episode_detail),
    path("portal/notifications/", portal_views.portal_notifications),
    path(
        "portal/notifications/<int:notification_id>/read/",
        csrf_exempt(portal_views.portal_notification_mark_read),
    ),
    path("portal/care-circle/", csrf_exempt(portal_views.portal_care_circle)),
    path(
        "portal/care-circle/<int:member_id>/",
        csrf_exempt(portal_views.portal_care_circle_detail),
    ),
    path("portal/consents/", csrf_exempt(portal_views.portal_consents)),
    path(
        "portal/consents/<int:consent_id>/revoke/",
        csrf_exempt(portal_views.portal_consent_revoke),
    ),
    path("conversations/", csrf_exempt(messaging_views.conversations_list)),
    path("conversations/<int:conversation_id>/", messaging_views.conversation_detail),
    path(
        "conversations/<int:conversation_id>/messages/",
        csrf_exempt(messaging_views.conversation_messages),
    ),
    path("messages/<int:message_id>/read/", csrf_exempt(messaging_views.message_mark_read)),
    path("auth/admin/audit/", csrf_exempt(auth_views.admin_auth_audit)),
    path("evidence/", csrf_exempt(evidence_item_views.evidence_list)),
    path("evidence/<int:evidence_id>/", evidence_item_views.evidence_detail),
    path("evidence/<int:evidence_id>/events/", evidence_item_views.evidence_events),
    path(
        "evidence/<int:evidence_id>/link/",
        csrf_exempt(evidence_item_views.evidence_link),
    ),
    path(
        "evidence/<int:evidence_id>/tag/",
        csrf_exempt(evidence_item_views.evidence_tag),
    ),
    path("appointments/", csrf_exempt(appointment_views.appointments_list)),
    path(
        "appointments/<int:appointment_id>/transition/",
        csrf_exempt(appointment_views.appointment_transition),
    ),
    path("tasks/", csrf_exempt(task_views.tasks_list)),
    path("tasks/<int:task_id>/assign/", csrf_exempt(task_views.task_assign)),
    path("tasks/<int:task_id>/complete/", csrf_exempt(task_views.task_complete)),
    path("patients/", csrf_exempt(patient_views.patients_list)),
    path("patients/search/", patient_views.patient_search),
    path("patients/<int:patient_id>/", patient_views.patient_detail),
    path("patients/<int:patient_id>/episodes/", patient_views.patient_episodes),
    path(
        "patients/<int:patient_id>/care-circle/",
        csrf_exempt(patient_views.patient_care_circle),
    ),
    path(
        "patients/<int:patient_id>/care-circle/<int:member_id>/",
        csrf_exempt(patient_views.patient_care_circle_detail),
    ),
    path(
        "patients/<int:patient_id>/consents/",
        csrf_exempt(patient_views.patient_consents),
    ),
    path(
        "patients/<int:patient_id>/consents/<int:consent_id>/revoke/",
        csrf_exempt(patient_views.patient_consent_revoke),
    ),
    path("patients/<int:patient_id>/merge/", csrf_exempt(patient_views.patient_merge)),
    path("episodes/", csrf_exempt(episode_views.episodes_list)),
    path("episodes/<int:episode_id>/", episode_views.episode_detail),
    path(
        "episodes/<int:episode_id>/transition/",
        csrf_exempt(episode_views.episode_transition),
    ),
    path("episodes/<int:episode_id>/timeline/", episode_views.episode_timeline),
    path(
        "episodes/<int:episode_id>/evidence/",
        csrf_exempt(evidence_item_views.episode_evidence_collection),
    ),
    path(
        "episodes/<int:episode_id>/evidence/<int:evidence_id>/",
        csrf_exempt(evidence_item_views.episode_evidence_link),
    ),
    path(
        "episodes/<int:episode_id>/evidence-pack/generate/",
        csrf_exempt(evidence_pack_views.evidence_pack_generate),
    ),
    path("work-items/", inbox_views.work_items_list),
    path("work-items/<int:item_id>/assign/", csrf_exempt(inbox_views.work_item_assign)),
    path(
        "work-items/<int:item_id>/complete/",
        csrf_exempt(inbox_views.work_item_complete),
    ),
    path("forms/templates/", form_views.form_templates),
    path("forms/responses/", csrf_exempt(form_views.form_responses)),
    path(
        "forms/responses/<int:response_id>/sign/",
        csrf_exempt(form_views.form_response_sign),
    ),
    path("evidence-packs/<int:pack_id>/", evidence_pack_views.evidence_pack_detail),
    path("patient/auth/request-otp/", csrf_exempt(patient_views.patient_request_otp)),
    path("patient/auth/verify-otp/", csrf_exempt(patient_views.patient_verify_otp)),
    path(
        "patient/medication-schedules/",
        csrf_exempt(patient_views.patient_schedules_list),
    ),
    path(
        "patient/medication-schedules/<int:schedule_id>/",
        csrf_exempt(patient_views.patient_schedule_detail),
    ),
    path(
        "patient/medication-schedules/<int:schedule_id>/confirm/",
        csrf_exempt(patient_views.patient_schedule_confirm),
    ),
    path("patient/feedback/", csrf_exempt(patient_views.patient_feedback)),
    path("patient/caregivers/", csrf_exempt(patient_views.patient_caregivers)),
    path("ai/", ai_views.ai_list),
    path("ai/triage/suggest/", csrf_exempt(ai_views.ai_triage_suggest)),
    path("ai/note/draft/", csrf_exempt(ai_views.ai_note_draft)),
    path(
        "ai/completeness/check/",
        csrf_exempt(ai_views.ai_completeness_check),
    ),
    path("ai/<int:artifact_id>/approve/", csrf_exempt(ai_views.ai_approve)),
    path("ai/<int:artifact_id>/reject/", csrf_exempt(ai_views.ai_reject)),
    path("ai/review/", csrf_exempt(ai_review_views.ai_review_collection)),
    path("ai/review/<int:review_id>/", ai_review_views.ai_review_detail),
    path("ai-review-items/", ai_review_views.ai_review_items_list),
    path(
        "ai-review-items/<int:item_id>/decide/",
        csrf_exempt(ai_review_views.ai_review_item_decide),
    ),
    path("interop/messages/", csrf_exempt(interop_views.interop_messages)),
    path("interop/process/", csrf_exempt(interop_views.interop_process)),
    path("metrics/", observability_views.metrics_snapshot),
    path(
        "episodes/<int:episode_id>/compliance/bundles/",
        csrf_exempt(compliance_views.episode_bundles),
    ),
    path(
        "compliance/bundles/<int:bundle_id>/download/",
        compliance_views.bundle_download,
    ),
    path("compliance/reports/", csrf_exempt(compliance_views.report_jobs)),
    path(
        "compliance/reports/<int:job_id>/run/",
        csrf_exempt(compliance_views.report_job_run),
    ),
    path("compliance/submissions/", csrf_exempt(compliance_views.submission_records)),
    path("privacy/consents/", csrf_exempt(privacy_views.consent_records)),
    path("privacy/dsar/exports/", privacy_views.dsar_exports),
    path("privacy/dsar/export/", csrf_exempt(privacy_views.dsar_export_request)),
    path("privacy/dsar/delete/", csrf_exempt(privacy_views.dsar_delete)),
    path(
        "privacy/dsar/exports/<int:export_id>/download/",
        privacy_views.dsar_export_download,
    ),
]

if settings.DEBUG:
    urlpatterns.append(path("sentry-debug/", observability_views.sentry_debug))
