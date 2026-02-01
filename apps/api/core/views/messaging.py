from __future__ import annotations

import json

from django.http import JsonResponse

from ..models import AuditEvent, Conversation, Episode, Membership, Message, MessageRead
from ..rbac import has_permission


def conversations_list(request):
    membership = request.membership  # type: ignore[attr-defined]
    if request.method == "POST":
        permission = has_permission(membership.role, "message:write")
        if not permission.allowed:
            return JsonResponse({"detail": "Not authorized."}, status=403)
        payload = json.loads(request.body or "{}")
        participants = payload.get("participants", [])
        if participants is None:
            participants = []
        if not isinstance(participants, list):
            return JsonResponse({"detail": "participants must be list"}, status=400)
        participant_ids = {int(pid) for pid in participants if str(pid).isdigit()}
        participant_ids.add(request.user.id)
        episode = None
        if payload.get("episode_id"):
            episode = Episode.objects.filter(
                organization=membership.organization, id=payload.get("episode_id")
            ).first()
            if not episode:
                return JsonResponse({"detail": "episode not found"}, status=404)
        member_ids = set(
            Membership.objects.filter(
                organization=membership.organization,
                is_active=True,
                user_id__in=participant_ids,
            ).values_list("user_id", flat=True)
        )
        if not member_ids:
            return JsonResponse({"detail": "participants not in org"}, status=400)
        conversation = Conversation.objects.create(
            organization=membership.organization, episode=episode
        )
        conversation.participants.set(list(member_ids))
        payload = {
            "id": conversation.id,
            "episode_id": conversation.episode_id,
            "participants": [
                {"id": user.id, "email": user.email, "username": user.username}
                for user in conversation.participants.all()
            ],
            "created_at": conversation.created_at.isoformat(),
        }
        return JsonResponse(payload, status=201)

    permission = has_permission(membership.role, "message:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    conversations = Conversation.objects.filter(
        organization=membership.organization, participants=request.user
    )
    episode_filter = request.GET.get("episode_id")
    if episode_filter:
        conversations = conversations.filter(episode_id=episode_filter)
    payload = [
        {
            "id": conversation.id,
            "episode_id": conversation.episode_id,
            "participants": [
                {"id": user.id, "email": user.email, "username": user.username}
                for user in conversation.participants.all()
            ],
            "created_at": conversation.created_at.isoformat(),
        }
        for conversation in conversations.order_by("-created_at")
    ]
    return JsonResponse({"results": payload})


def conversation_detail(request, conversation_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "message:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    conversation = Conversation.objects.filter(
        organization=membership.organization,
        id=conversation_id,
        participants=request.user,
    ).first()
    if not conversation:
        return JsonResponse({"detail": "Not found."}, status=404)
    messages = Message.objects.filter(
        organization=membership.organization, conversation=conversation
    ).order_by("created_at", "id")
    payload = {
        "id": conversation.id,
        "episode_id": conversation.episode_id,
        "participants": [
            {"id": user.id, "email": user.email, "username": user.username}
            for user in conversation.participants.all()
        ],
        "messages": [
            {
                "id": message.id,
                "sender_id": message.sender_id,
                "body": message.body,
                "created_at": message.created_at.isoformat(),
                "read": MessageRead.objects.filter(
                    message=message, reader=request.user
                ).exists(),
            }
            for message in messages
        ],
    }
    return JsonResponse(payload)


def conversation_messages(request, conversation_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "message:write")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    conversation = Conversation.objects.filter(
        organization=membership.organization,
        id=conversation_id,
        participants=request.user,
    ).first()
    if not conversation:
        return JsonResponse({"detail": "Not found."}, status=404)
    payload = json.loads(request.body or "{}")
    body = str(payload.get("body", "")).strip()
    if not body:
        return JsonResponse({"detail": "body is required"}, status=400)
    message = Message.objects.create(
        organization=membership.organization,
        conversation=conversation,
        sender=request.user,
        body=body,
    )
    AuditEvent.objects.create(
        organization=membership.organization,
        actor=request.user,
        action="message.sent",
        target_type="Message",
        target_id=str(message.id),
        metadata={"conversation_id": conversation.id},
    )
    return JsonResponse(
        {
            "id": message.id,
            "sender_id": message.sender_id,
            "body": message.body,
            "created_at": message.created_at.isoformat(),
        },
        status=201,
    )


def message_mark_read(request, message_id: int):
    membership = request.membership  # type: ignore[attr-defined]
    permission = has_permission(membership.role, "message:read")
    if not permission.allowed:
        return JsonResponse({"detail": "Not authorized."}, status=403)
    message = Message.objects.filter(
        organization=membership.organization, id=message_id
    ).select_related("conversation").first()
    if not message or not message.conversation.participants.filter(
        id=request.user.id
    ).exists():
        return JsonResponse({"detail": "Not found."}, status=404)
    read, _ = MessageRead.objects.get_or_create(
        organization=membership.organization,
        message=message,
        reader=request.user,
    )
    return JsonResponse({"id": message.id, "read_at": read.read_at.isoformat()})
