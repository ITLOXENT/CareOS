from __future__ import annotations


def build_openapi_spec() -> dict:
    return {
        "openapi": "3.0.3",
        "info": {"title": "CareOS API", "version": "0.1.0"},
        "servers": [{"url": "http://localhost:8000"}],
        "paths": {
            "/health/": {
                "get": {
                    "summary": "Health check",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/HealthResponse"}
                                }
                            },
                        }
                    },
                }
            },
            "/me/": {
                "get": {
                    "summary": "Current user",
                    "security": [{"cookieAuth": []}],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/MeResponse"}
                                }
                            },
                        }
                    },
                }
            },
            "/orgs/current/": {
                "get": {
                    "summary": "Current organization",
                    "security": [{"cookieAuth": []}],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/OrgResponse"}
                                }
                            },
                        }
                    },
                },
                "patch": {
                    "summary": "Update organization profile",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/OrgProfileUpdateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/OrgResponse"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                },
            },
            "/orgs/members/": {
                "get": {
                    "summary": "List organization members",
                    "security": [{"cookieAuth": []}],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/OrgMemberList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                }
            },
            "/orgs/invites/": {
                "get": {
                    "summary": "List organization invites",
                    "security": [{"cookieAuth": []}],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/OrgInviteList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                },
                "post": {
                    "summary": "Create organization invite",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/OrgInviteRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/OrgInviteResponse"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                    },
                },
            },
            "/orgs/members/{member_id}/role/": {
                "post": {
                    "summary": "Change member role",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "member_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/OrgMemberRoleRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/OrgMemberRoleResponse"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/orgs/members/{member_id}/deactivate/": {
                "post": {
                    "summary": "Deactivate member",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "member_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/OrgMemberDeactivateResponse"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/audit-events/": {
                "get": {
                    "summary": "Audit events",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {"in": "query", "name": "actor", "schema": {"type": "string"}},
                        {"in": "query", "name": "action", "schema": {"type": "string"}},
                        {"in": "query", "name": "resource", "schema": {"type": "string"}},
                        {"in": "query", "name": "target_type", "schema": {"type": "string"}},
                        {"in": "query", "name": "target_id", "schema": {"type": "string"}},
                        {"in": "query", "name": "from", "schema": {"type": "string"}},
                        {"in": "query", "name": "to", "schema": {"type": "string"}},
                        {"in": "query", "name": "start", "schema": {"type": "string"}},
                        {"in": "query", "name": "end", "schema": {"type": "string"}},
                        {"in": "query", "name": "page", "schema": {"type": "integer"}},
                        {"in": "query", "name": "page_size", "schema": {"type": "integer"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AuditEventList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                }
            },
            "/healthz/": {
                "get": {
                    "summary": "Health check",
                    "responses": {"200": {"description": "OK"}},
                }
            },
            "/readyz/": {
                "get": {
                    "summary": "Readiness check",
                    "responses": {
                        "200": {"description": "OK"},
                        "503": {"description": "Unavailable"},
                    },
                }
            },
            "/metrics/": {
                "get": {
                    "summary": "Metrics snapshot",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/MetricsResponse"}
                                }
                            },
                        }
                    },
                }
            },
            "/billing/plans/": {
                "get": {
                    "summary": "Billing plans",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {"in": "query", "name": "currency", "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/BillingPlanList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                }
            },
            "/billing/checkout-session/": {
                "post": {
                    "summary": "Create checkout session",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/BillingCheckoutRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/BillingCheckoutResponse"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                    },
                }
            },
            "/billing/subscription/": {
                "get": {
                    "summary": "Billing subscription",
                    "security": [{"cookieAuth": []}],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/BillingSubscription"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                }
            },
            "/billing/webhook/": {
                "post": {
                    "summary": "Billing webhook",
                    "responses": {
                        "200": {"description": "OK"},
                        "400": {"description": "Bad request"},
                    },
                }
            },
            "/integrations/": {
                "get": {
                    "summary": "List integrations",
                    "security": [{"cookieAuth": []}],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/IntegrationListResponse"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                }
            },
            "/integrations/{provider}/connect/": {
                "post": {
                    "summary": "Connect integration",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "provider",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/IntegrationConnectRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/IntegrationResponse"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                    },
                }
            },
            "/integrations/{provider}/test/": {
                "post": {
                    "summary": "Test integration",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "provider",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/IntegrationTestResponse"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/integrations/{provider}/disconnect/": {
                "post": {
                    "summary": "Disconnect integration",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "provider",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/IntegrationResponse"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/integrations/api-keys/": {
                "get": {
                    "summary": "List integration API keys",
                    "security": [{"cookieAuth": []}],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/IntegrationApiKeyList"
                                    }
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                },
                "post": {
                    "summary": "Create integration API key",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/IntegrationApiKeyCreateRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/IntegrationApiKeyCreateResponse"
                                    }
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                    },
                },
            },
            "/integrations/api-keys/{key_id}/revoke/": {
                "post": {
                    "summary": "Revoke integration API key",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "key_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/IntegrationApiKeyRevokeResponse"
                                    }
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/privacy/consents/": {
                "get": {
                    "summary": "List consent records",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {"in": "query", "name": "subject_type", "schema": {"type": "string"}},
                        {"in": "query", "name": "subject_id", "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ConsentRecordList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                },
                "post": {
                    "summary": "Create consent record",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ConsentRecordCreateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ConsentRecord"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                    },
                },
            },
            "/privacy/dsar/exports/": {
                "get": {
                    "summary": "List DSAR exports",
                    "security": [{"cookieAuth": []}],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/DsarExportList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                }
            },
            "/privacy/dsar/export/": {
                "post": {
                    "summary": "Request DSAR export",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/DsarExportRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/DsarExport"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                    },
                }
            },
            "/privacy/dsar/delete/": {
                "post": {
                    "summary": "Request DSAR delete",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/DsarDeleteRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {"description": "OK"},
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/privacy/dsar/exports/{export_id}/download/": {
                "get": {
                    "summary": "Download DSAR export",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "export_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "OK"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/ai/review/": {
                "get": {
                    "summary": "List AI review requests",
                    "security": [{"cookieAuth": []}],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AIReviewListResponse"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                },
                "post": {
                    "summary": "Create AI review request",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AIReviewCreateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AIReviewCreateResponse"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                    },
                },
            },
            "/ai/review/{review_id}/": {
                "get": {
                    "summary": "AI review detail",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "review_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AIReviewDetail"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/ai-review-items/": {
                "get": {
                    "summary": "List AI review items",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {"in": "query", "name": "status", "schema": {"type": "string"}},
                        {"in": "query", "name": "pending_only", "schema": {"type": "string"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AIReviewItemList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                }
            },
            "/ai-review-items/{item_id}/decide/": {
                "post": {
                    "summary": "Decide AI review item",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "item_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AIReviewItemDecision"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AIReviewItemDecisionResponse"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/portal/auth/accept-invite/": {
                "post": {
                    "summary": "Accept portal invite",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PortalAuthResponse"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "404": {"description": "Not found"},
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PortalAcceptInviteRequest"}
                            }
                        }
                    },
                }
            },
            "/portal/auth/login/": {
                "post": {
                    "summary": "Portal login",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PortalAuthResponse"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "404": {"description": "Not found"},
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PortalLoginRequest"}
                            }
                        }
                    },
                }
            },
            "/auth/admin/audit/": {
                "post": {
                    "summary": "Admin auth audit event",
                    "responses": {
                        "200": {"description": "OK"},
                        "400": {"description": "Bad request"},
                        "403": {"description": "Unauthorized"},
                        "404": {"description": "Not found"},
                    },
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AdminAuthAuditRequest"}
                            }
                        }
                    },
                }
            },
            "/portal/me/": {
                "get": {
                    "summary": "Portal profile",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PortalMeResponse"}
                                }
                            },
                        },
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/portal/episodes/": {
                "get": {
                    "summary": "Portal episodes",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PortalEpisodeList"}
                                }
                            },
                        },
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/portal/episodes/{episode_id}/": {
                "get": {
                    "summary": "Portal episode detail",
                    "parameters": [
                        {
                            "in": "path",
                            "name": "episode_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PortalEpisodeDetail"}
                                }
                            },
                        },
                        "401": {"description": "Unauthorized"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/portal/notifications/": {
                "get": {
                    "summary": "Portal notifications",
                    "parameters": [
                        {"in": "query", "name": "unread_only", "schema": {"type": "boolean"}},
                        {"in": "query", "name": "page", "schema": {"type": "integer"}},
                        {"in": "query", "name": "page_size", "schema": {"type": "integer"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PortalNotificationList"}
                                }
                            },
                        },
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/portal/notifications/{notification_id}/read/": {
                "post": {
                    "summary": "Mark portal notification read",
                    "parameters": [
                        {
                            "in": "path",
                            "name": "notification_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/PortalNotificationReadResponse"
                                    }
                                }
                            },
                        },
                        "401": {"description": "Unauthorized"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/portal/care-circle/": {
                "get": {
                    "summary": "Portal care circle",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CareCircleListResponse"}
                                }
                            },
                        },
                        "401": {"description": "Unauthorized"},
                    },
                },
                "post": {
                    "summary": "Create portal care circle member",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/CareCircleMemberCreateRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CareCircleMember"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "401": {"description": "Unauthorized"},
                    },
                },
            },
            "/portal/care-circle/{member_id}/": {
                "patch": {
                    "summary": "Update portal care circle member",
                    "parameters": [
                        {
                            "in": "path",
                            "name": "member_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/CareCircleMemberUpdateRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CareCircleMember"}
                                }
                            },
                        },
                        "401": {"description": "Unauthorized"},
                        "404": {"description": "Not found"},
                    },
                },
                "delete": {
                    "summary": "Delete portal care circle member",
                    "parameters": [
                        {
                            "in": "path",
                            "name": "member_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "OK"},
                        "401": {"description": "Unauthorized"},
                        "404": {"description": "Not found"},
                    },
                },
            },
            "/portal/consents/": {
                "get": {
                    "summary": "Portal consents",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/PatientConsentListResponse"
                                    }
                                }
                            },
                        },
                        "401": {"description": "Unauthorized"},
                    },
                },
                "post": {
                    "summary": "Create portal consent",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/PatientConsentCreateRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PatientConsent"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "401": {"description": "Unauthorized"},
                    },
                },
            },
            "/portal/consents/{consent_id}/revoke/": {
                "post": {
                    "summary": "Revoke portal consent",
                    "parameters": [
                        {
                            "in": "path",
                            "name": "consent_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PatientConsent"}
                                }
                            },
                        },
                        "401": {"description": "Unauthorized"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/conversations/": {
                "get": {
                    "summary": "List conversations",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {"in": "query", "name": "episode_id", "schema": {"type": "integer"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ConversationListResponse"
                                    }
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                },
                "post": {
                    "summary": "Create conversation",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/ConversationCreateRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Conversation"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                    },
                },
            },
            "/conversations/{conversation_id}/": {
                "get": {
                    "summary": "Conversation detail",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "conversation_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ConversationDetailResponse"
                                    }
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/conversations/{conversation_id}/messages/": {
                "post": {
                    "summary": "Send message",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "conversation_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MessageCreateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Message"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/messages/{message_id}/read/": {
                "post": {
                    "summary": "Mark message read",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "message_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/MessageReadResponse"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/notifications/": {
                "get": {
                    "summary": "List notifications",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "query",
                            "name": "unread_only",
                            "schema": {"type": "string"},
                        },
                        {"in": "query", "name": "page", "schema": {"type": "integer"}},
                        {"in": "query", "name": "page_size", "schema": {"type": "integer"}},
                        {"in": "query", "name": "limit", "schema": {"type": "integer"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/NotificationList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                }
            },
            "/notifications/{notification_id}/read/": {
                "post": {
                    "summary": "Mark notification read",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "notification_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/NotificationReadResponse"
                                    }
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/exports/": {
                "get": {
                    "summary": "List exports",
                    "security": [{"cookieAuth": []}],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ExportJobList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                },
                "post": {
                    "summary": "Request export",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ExportJobRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ExportJob"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                    },
                },
            },
            "/exports/{export_id}/": {
                "get": {
                    "summary": "Export detail",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "export_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ExportJob"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/exports/{export_id}/download/": {
                "get": {
                    "summary": "Download export",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "export_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "OK"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/episodes/": {
                "get": {
                    "summary": "List episodes",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {"in": "query", "name": "status", "schema": {"type": "string"}},
                        {"in": "query", "name": "assigned_to", "schema": {"type": "string"}},
                        {"in": "query", "name": "created_by", "schema": {"type": "string"}},
                        {"in": "query", "name": "search", "schema": {"type": "string"}},
                        {"in": "query", "name": "page", "schema": {"type": "integer"}},
                        {"in": "query", "name": "page_size", "schema": {"type": "integer"}},
                        {"in": "query", "name": "limit", "schema": {"type": "integer"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EpisodeList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                },
                "post": {
                    "summary": "Create episode",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/EpisodeCreateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Episode"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                    },
                },
            },
            "/episodes/{episode_id}/": {
                "get": {
                    "summary": "Episode detail",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "episode_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Episode"}
                                }
                            },
                        },
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/episodes/{episode_id}/transition/": {
                "post": {
                    "summary": "Transition episode",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "episode_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/EpisodeTransitionRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/EpisodeTransitionResponse"
                                    }
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/episodes/{episode_id}/timeline/": {
                "get": {
                    "summary": "Episode timeline",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "episode_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                        {"in": "query", "name": "page", "schema": {"type": "integer"}},
                        {"in": "query", "name": "page_size", "schema": {"type": "integer"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/EpisodeTimelineResponse"
                                    }
                                }
                            },
                        },
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/episodes/{episode_id}/evidence/": {
                "get": {
                    "summary": "List episode evidence",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "episode_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EvidenceListResponse"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                },
                "post": {
                    "summary": "Create episode evidence",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "episode_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "multipart/form-data": {
                                "schema": {"$ref": "#/components/schemas/EvidenceCreateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EvidenceItem"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                },
            },
            "/episodes/{episode_id}/evidence/{evidence_id}/": {
                "post": {
                    "summary": "Link evidence to episode",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "episode_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                        {
                            "in": "path",
                            "name": "evidence_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EvidenceLinkResponse"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/episodes/{episode_id}/compliance/bundles/": {
                "get": {
                    "summary": "List compliance bundles",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "episode_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EvidenceBundleList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                },
                "post": {
                    "summary": "Generate compliance bundle",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "episode_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EvidenceBundle"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                },
            },
            "/compliance/bundles/{bundle_id}/download/": {
                "get": {
                    "summary": "Download compliance bundle",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "bundle_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "OK"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/compliance/reports/": {
                "get": {
                    "summary": "List report jobs",
                    "security": [{"cookieAuth": []}],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ReportJobList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                },
                "post": {
                    "summary": "Create report job",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ReportJobCreateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ReportJob"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                    },
                },
            },
            "/compliance/reports/{job_id}/run/": {
                "post": {
                    "summary": "Run report job",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "job_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/ReportJob"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/compliance/submissions/": {
                "get": {
                    "summary": "List submission records",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {"in": "query", "name": "episode_id", "schema": {"type": "integer"}}
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/SubmissionRecordList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                },
                "post": {
                    "summary": "Create submission record",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/SubmissionRecordCreateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/SubmissionRecord"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                    },
                },
            },
            "/evidence/{evidence_id}/events/": {
                "get": {
                    "summary": "Evidence events",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "evidence_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                        {"in": "query", "name": "page", "schema": {"type": "integer"}},
                        {"in": "query", "name": "page_size", "schema": {"type": "integer"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EvidenceEventList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/work-items/": {
                "get": {
                    "summary": "List work items",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {"in": "query", "name": "status", "schema": {"type": "string"}},
                        {"in": "query", "name": "assignee", "schema": {"type": "string"}},
                        {"in": "query", "name": "due_before", "schema": {"type": "string"}},
                        {"in": "query", "name": "kind", "schema": {"type": "string"}},
                        {"in": "query", "name": "appointment_id", "schema": {"type": "integer"}},
                        {
                            "in": "query",
                            "name": "appointment",
                            "schema": {"type": "string"},
                        },
                        {"in": "query", "name": "page", "schema": {"type": "integer"}},
                        {"in": "query", "name": "page_size", "schema": {"type": "integer"}},
                        {"in": "query", "name": "limit", "schema": {"type": "integer"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/WorkItemListResponse"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                }
            },
            "/work-items/{item_id}/assign/": {
                "post": {
                    "summary": "Assign work item",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "item_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/WorkItemAssignRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/WorkItemAssignResponse"
                                    }
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/work-items/{item_id}/complete/": {
                "post": {
                    "summary": "Complete work item",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "item_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/WorkItemCompleteResponse"
                                    }
                                }
                            },
                        },
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/appointments/": {
                "get": {
                    "summary": "List appointments",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {"in": "query", "name": "status", "schema": {"type": "string"}},
                        {"in": "query", "name": "patient_id", "schema": {"type": "integer"}},
                        {"in": "query", "name": "episode_id", "schema": {"type": "integer"}},
                        {"in": "query", "name": "scheduled_before", "schema": {"type": "string"}},
                        {"in": "query", "name": "scheduled_after", "schema": {"type": "string"}},
                        {"in": "query", "name": "page", "schema": {"type": "integer"}},
                        {"in": "query", "name": "page_size", "schema": {"type": "integer"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/AppointmentListResponse"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                },
                "post": {
                    "summary": "Create appointment",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/AppointmentCreateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Appointment"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                },
            },
            "/appointments/{appointment_id}/transition/": {
                "post": {
                    "summary": "Transition appointment",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "appointment_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/AppointmentTransitionRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/AppointmentTransitionResponse"
                                    }
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/tasks/": {
                "get": {
                    "summary": "List tasks",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {"in": "query", "name": "status", "schema": {"type": "string"}},
                        {"in": "query", "name": "priority", "schema": {"type": "string"}},
                        {"in": "query", "name": "episode_id", "schema": {"type": "integer"}},
                        {"in": "query", "name": "work_item_id", "schema": {"type": "integer"}},
                        {"in": "query", "name": "due_before", "schema": {"type": "string"}},
                        {"in": "query", "name": "page", "schema": {"type": "integer"}},
                        {"in": "query", "name": "page_size", "schema": {"type": "integer"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/TaskListResponse"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                },
                "post": {
                    "summary": "Create task",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/TaskCreateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Task"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                },
            },
            "/tasks/{task_id}/assign/": {
                "post": {
                    "summary": "Assign task",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "task_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/TaskAssignRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/TaskAssignResponse"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/tasks/{task_id}/complete/": {
                "post": {
                    "summary": "Complete task",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "task_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/TaskCompleteResponse"}
                                }
                            },
                        },
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/patients/": {
                "get": {
                    "summary": "List patients",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {"in": "query", "name": "search", "schema": {"type": "string"}},
                        {"in": "query", "name": "page", "schema": {"type": "integer"}},
                        {"in": "query", "name": "page_size", "schema": {"type": "integer"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PatientList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                },
                "post": {
                    "summary": "Create patient",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PatientCreateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Patient"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                    },
                },
            },
            "/patients/{patient_id}/": {
                "get": {
                    "summary": "Patient detail",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "patient_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Patient"}
                                }
                            },
                        },
                        "404": {"description": "Not found"},
                    },
                },
                "patch": {
                    "summary": "Update patient",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "patient_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PatientUpdateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Patient"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                },
            },
            "/patients/search/": {
                "get": {
                    "summary": "Search patients",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {"in": "query", "name": "q", "schema": {"type": "string"}},
                        {"in": "query", "name": "page", "schema": {"type": "integer"}},
                        {"in": "query", "name": "page_size", "schema": {"type": "integer"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PatientList"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                }
            },
            "/patients/{patient_id}/episodes/": {
                "get": {
                    "summary": "Patient episodes",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "patient_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PatientEpisodesResponse"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/patients/{patient_id}/care-circle/": {
                "get": {
                    "summary": "List care circle",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "patient_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CareCircleListResponse"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                },
                "post": {
                    "summary": "Create care circle member",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "patient_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/CareCircleMemberCreateRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CareCircleMember"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                },
            },
            "/patients/{patient_id}/care-circle/{member_id}/": {
                "patch": {
                    "summary": "Update care circle member",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "patient_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                        {
                            "in": "path",
                            "name": "member_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/CareCircleMemberUpdateRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CareCircleMember"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                },
                "delete": {
                    "summary": "Delete care circle member",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "patient_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                        {
                            "in": "path",
                            "name": "member_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                    ],
                    "responses": {
                        "200": {"description": "OK"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                },
            },
            "/patients/{patient_id}/consents/": {
                "get": {
                    "summary": "List patient consents",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "patient_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/PatientConsentListResponse"
                                    }
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                },
                "post": {
                    "summary": "Grant patient consent",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "patient_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/PatientConsentCreateRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PatientConsent"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                },
            },
            "/patients/{patient_id}/consents/{consent_id}/revoke/": {
                "post": {
                    "summary": "Revoke patient consent",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "patient_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                        {
                            "in": "path",
                            "name": "consent_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PatientConsent"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/patients/{patient_id}/merge/": {
                "post": {
                    "summary": "Merge patient",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "patient_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PatientMergeRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/PatientMergeResponse"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/evidence/": {
                "get": {
                    "summary": "List evidence",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {"in": "query", "name": "episode", "schema": {"type": "string"}},
                        {"in": "query", "name": "patient", "schema": {"type": "string"}},
                        {"in": "query", "name": "kind", "schema": {"type": "string"}},
                        {"in": "query", "name": "tags", "schema": {"type": "string"}},
                        {"in": "query", "name": "page", "schema": {"type": "integer"}},
                        {"in": "query", "name": "page_size", "schema": {"type": "integer"}},
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EvidenceListResponse"}
                                }
                            },
                        },
                        "403": {"description": "Forbidden"},
                    },
                },
                "post": {
                    "summary": "Create evidence",
                    "security": [{"cookieAuth": []}],
                    "requestBody": {
                        "content": {
                            "multipart/form-data": {
                                "schema": {"$ref": "#/components/schemas/EvidenceCreateRequest"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EvidenceItem"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                    },
                },
            },
            "/evidence/{evidence_id}/": {
                "get": {
                    "summary": "Evidence detail",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "evidence_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        },
                        {
                            "in": "query",
                            "name": "download",
                            "schema": {"type": "string"},
                            "description": "Set to 1 to download the file",
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EvidenceItem"}
                                }
                            },
                        },
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/evidence/{evidence_id}/link/": {
                "post": {
                    "summary": "Link evidence",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "evidence_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/EvidenceLinkRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EvidenceLinkResponse"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
            "/evidence/{evidence_id}/tag/": {
                "post": {
                    "summary": "Tag evidence",
                    "security": [{"cookieAuth": []}],
                    "parameters": [
                        {
                            "in": "path",
                            "name": "evidence_id",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/EvidenceTagRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/EvidenceTagResponse"}
                                }
                            },
                        },
                        "400": {"description": "Bad request"},
                        "403": {"description": "Forbidden"},
                        "404": {"description": "Not found"},
                    },
                }
            },
        },
        "components": {
            "schemas": {
                "HealthResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "timestamp": {"type": "string"},
                        "version": {"type": "string"},
                        "build_sha": {"type": "string"},
                        "db_ok": {"type": "boolean"},
                    },
                    "required": ["status", "timestamp", "version", "build_sha", "db_ok"],
                },
                "MeResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "email": {"type": ["string", "null"]},
                        "organization_id": {"type": "integer"},
                        "role": {"type": "string"},
                    },
                    "required": ["id", "email", "organization_id", "role"],
                },
                "OrgResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "slug": {"type": "string"},
                    },
                    "required": ["id", "name", "slug"],
                },
                "OrgProfileUpdateRequest": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                },
                "OrgMember": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "user_id": {"type": "integer"},
                        "email": {"type": "string"},
                        "username": {"type": "string"},
                        "role": {"type": "string"},
                        "is_active": {"type": "boolean"},
                    },
                    "required": ["id", "user_id", "email", "role", "is_active"],
                },
                "OrgMemberList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/OrgMember"},
                        }
                    },
                    "required": ["results"],
                },
                "OrgInvite": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "email": {"type": "string"},
                        "role": {"type": "string"},
                        "expires_at": {"type": "string"},
                        "created_at": {"type": "string"},
                    },
                    "required": ["id", "email", "role", "expires_at", "created_at"],
                },
                "OrgInviteList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/OrgInvite"},
                        }
                    },
                    "required": ["results"],
                },
                "OrgInviteRequest": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "role": {"type": "string"},
                        "expires_in_hours": {"type": "integer"},
                    },
                    "required": ["email"],
                },
                "OrgInviteResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "email": {"type": "string"},
                        "role": {"type": "string"},
                        "expires_at": {"type": "string"},
                        "token": {"type": "string"},
                    },
                    "required": ["id", "email", "role", "expires_at", "token"],
                },
                "OrgMemberRoleRequest": {
                    "type": "object",
                    "properties": {"role": {"type": "string"}},
                    "required": ["role"],
                },
                "OrgMemberRoleResponse": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}, "role": {"type": "string"}},
                    "required": ["id", "role"],
                },
                "OrgMemberDeactivateResponse": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}, "is_active": {"type": "boolean"}},
                    "required": ["id", "is_active"],
                },
                "AuditEvent": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "action": {"type": "string"},
                        "target_type": {"type": "string"},
                        "target_id": {"type": "string"},
                        "actor_id": {"type": ["integer", "null"]},
                        "metadata": {"type": "object"},
                        "request_id": {"type": "string"},
                        "created_at": {"type": "string"},
                    },
                    "required": [
                        "id",
                        "action",
                        "target_type",
                        "target_id",
                        "created_at",
                    ],
                },
                "AuditEventList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/AuditEvent"},
                        },
                        "count": {"type": "integer"},
                        "page": {"type": "integer"},
                        "page_size": {"type": "integer"},
                    },
                    "required": ["results", "count", "page", "page_size"],
                },
                "MetricsResponse": {
                    "type": "object",
                    "properties": {
                        "total_requests": {"type": "integer"},
                        "last_duration_ms": {"type": "number"},
                    },
                    "required": ["total_requests", "last_duration_ms"],
                },
                "PortalAcceptInviteRequest": {
                    "type": "object",
                    "properties": {"token": {"type": "string"}},
                    "required": ["token"],
                },
                "PortalLoginRequest": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                    },
                },
                "AdminAuthAuditRequest": {
                    "type": "object",
                    "properties": {
                        "outcome": {"type": "string"},
                        "username": {"type": "string"},
                    },
                    "required": ["outcome", "username"],
                },
                "PortalAuthResponse": {
                    "type": "object",
                    "properties": {
                        "token": {"type": "string"},
                        "role": {"type": "string"},
                        "patient_id": {"type": "integer"},
                        "organization_id": {"type": "integer"},
                        "expires_at": {"type": "string"},
                    },
                    "required": ["token", "role", "patient_id", "organization_id", "expires_at"],
                },
                "PortalMeResponse": {
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "integer"},
                        "organization_id": {"type": "integer"},
                        "role": {"type": "string"},
                        "given_name": {"type": "string"},
                        "family_name": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                    },
                    "required": ["patient_id", "organization_id", "role"],
                },
                "PortalEpisode": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "status": {"type": "string"},
                        "created_at": {"type": "string"},
                        "updated_at": {"type": "string"},
                    },
                    "required": ["id", "title", "status", "created_at", "updated_at"],
                },
                "PortalEpisodeList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/PortalEpisode"},
                        }
                    },
                    "required": ["results"],
                },
                "PortalEpisodeEvent": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "event_type": {"type": "string"},
                        "from_state": {"type": "string"},
                        "to_state": {"type": "string"},
                        "note": {"type": "string"},
                        "created_at": {"type": "string"},
                    },
                    "required": ["id", "event_type", "created_at"],
                },
                "PortalEpisodeDetail": {
                    "type": "object",
                    "properties": {
                        "episode": {"$ref": "#/components/schemas/PortalEpisode"},
                        "timeline": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/PortalEpisodeEvent"},
                        },
                    },
                    "required": ["episode", "timeline"],
                },
                "PortalNotification": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "kind": {"type": "string"},
                        "title": {"type": "string"},
                        "body": {"type": "string"},
                        "url": {"type": "string"},
                        "unread": {"type": "boolean"},
                        "read_at": {"type": ["string", "null"]},
                        "created_at": {"type": "string"},
                    },
                    "required": ["id", "title", "unread", "created_at"],
                },
                "PortalNotificationList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/PortalNotification"},
                        },
                        "count": {"type": "integer"},
                        "page": {"type": "integer"},
                        "page_size": {"type": "integer"},
                    },
                    "required": ["results", "count", "page", "page_size"],
                },
                "PortalNotificationReadResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "unread": {"type": "boolean"},
                        "read_at": {"type": ["string", "null"]},
                    },
                    "required": ["id", "unread"],
                },
                "BillingPlan": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "name": {"type": "string"},
                        "seats": {"type": "integer"},
                        "currency": {"type": "string"},
                        "entitlements": {"type": "object"},
                    },
                    "required": ["code", "name", "seats"],
                },
                "BillingPlanList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/BillingPlan"},
                        }
                    },
                    "required": ["results"],
                },
                "BillingCheckoutRequest": {
                    "type": "object",
                    "properties": {
                        "plan_code": {"type": "string"},
                        "success_url": {"type": "string"},
                        "cancel_url": {"type": "string"},
                        "currency": {"type": "string"},
                    },
                    "required": ["plan_code", "success_url", "cancel_url"],
                },
                "BillingCheckoutResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "url": {"type": "string"},
                    },
                    "required": ["id", "url"],
                },
                "BillingSubscription": {
                    "type": "object",
                    "properties": {
                        "plan_code": {"type": "string"},
                        "status": {"type": "string"},
                        "current_period_end": {"type": ["string", "null"]},
                        "seat_limit": {"type": "integer"},
                        "entitlements": {"type": "object"},
                        "currency": {"type": ["string", "null"]},
                    },
                    "required": ["status"],
                },
                "Integration": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "provider": {"type": "string"},
                        "status": {"type": "string"},
                        "last_tested_at": {"type": ["string", "null"]},
                        "last_error": {"type": "string"},
                        "config": {"type": "object"},
                    },
                    "required": ["id", "provider", "status"],
                },
                "IntegrationListResponse": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Integration"},
                        }
                    },
                    "required": ["results"],
                },
                "IntegrationApiKey": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "prefix": {"type": "string"},
                        "created_at": {"type": "string"},
                        "revoked_at": {"type": ["string", "null"]},
                        "created_by": {"type": ["integer", "null"]},
                    },
                    "required": ["id", "name", "prefix", "created_at"],
                },
                "IntegrationApiKeyList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/IntegrationApiKey"},
                        }
                    },
                    "required": ["results"],
                },
                "IntegrationApiKeyCreateRequest": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
                "IntegrationApiKeyCreateResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "prefix": {"type": "string"},
                        "created_at": {"type": "string"},
                        "revoked_at": {"type": ["string", "null"]},
                        "token": {"type": "string"},
                    },
                    "required": ["id", "name", "prefix", "created_at", "token"],
                },
                "IntegrationApiKeyRevokeResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "revoked_at": {"type": ["string", "null"]},
                    },
                    "required": ["id", "revoked_at"],
                },
                "ConsentRecord": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "patient_id": {"type": ["integer", "null"]},
                        "subject_type": {"type": "string"},
                        "subject_id": {"type": "string"},
                        "consent_type": {"type": "string"},
                        "scope": {"type": "string"},
                        "lawful_basis": {"type": "string"},
                        "granted_by": {"type": "string"},
                        "expires_at": {"type": ["string", "null"]},
                        "policy_version": {"type": "string"},
                        "channel": {"type": "string"},
                        "granted": {"type": "boolean"},
                        "revoked_at": {"type": ["string", "null"]},
                        "metadata": {"type": "object"},
                        "recorded_at": {"type": "string"},
                        "created_at": {"type": "string"},
                    },
                    "required": [
                        "id",
                        "subject_type",
                        "subject_id",
                        "consent_type",
                        "policy_version",
                        "granted",
                        "recorded_at",
                        "created_at",
                    ],
                },
                "ConsentRecordList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ConsentRecord"},
                        }
                    },
                    "required": ["results"],
                },
                "ConsentRecordCreateRequest": {
                    "type": "object",
                    "properties": {
                        "subject_type": {"type": "string"},
                        "subject_id": {"type": "string"},
                        "consent_type": {"type": "string"},
                        "policy_version": {"type": "string"},
                        "channel": {"type": "string"},
                        "granted": {"type": "boolean"},
                        "metadata": {"type": "object"},
                    },
                    "required": ["subject_type", "subject_id", "consent_type", "policy_version"],
                },
                "DsarExport": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "subject_type": {"type": "string"},
                        "subject_id": {"type": "string"},
                        "status": {"type": "string"},
                        "created_at": {"type": "string"},
                        "finished_at": {"type": ["string", "null"]},
                        "artifact_path": {"type": ["string", "null"]},
                    },
                    "required": ["id", "subject_type", "subject_id", "status", "created_at"],
                },
                "DsarExportList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/DsarExport"},
                        }
                    },
                    "required": ["results"],
                },
                "DsarExportRequest": {
                    "type": "object",
                    "properties": {
                        "subject_type": {"type": "string"},
                        "subject_id": {"type": "string"},
                    },
                },
                "DsarDeleteRequest": {
                    "type": "object",
                    "properties": {
                        "subject_type": {"type": "string"},
                        "subject_id": {"type": "string"},
                    },
                    "required": ["subject_type", "subject_id"],
                },
                "IntegrationConnectRequest": {
                    "type": "object",
                    "properties": {
                        "api_key": {"type": "string"},
                        "sender": {"type": "string"},
                    },
                    "required": ["api_key", "sender"],
                },
                "IntegrationResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "provider": {"type": "string"},
                        "status": {"type": "string"},
                    },
                    "required": ["id", "provider", "status"],
                },
                "IntegrationTestResponse": {
                    "type": "object",
                    "properties": {
                        "provider": {"type": "string"},
                        "status": {"type": "string"},
                        "tested_at": {"type": "string"},
                    },
                    "required": ["provider", "status", "tested_at"],
                },
                "AIReviewCreateRequest": {
                    "type": "object",
                    "properties": {
                        "input_type": {"type": "string"},
                        "payload": {"type": "object"},
                    },
                    "required": ["input_type"],
                },
                "AIReviewCreateResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "status": {"type": "string"},
                        "input_type": {"type": "string"},
                        "created_at": {"type": "string"},
                    },
                    "required": ["id", "status", "input_type", "created_at"],
                },
                "AIReviewDetail": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "input_type": {"type": "string"},
                        "payload": {"type": "object"},
                        "status": {"type": "string"},
                        "output": {"type": "object"},
                        "model_provider": {"type": "string"},
                        "model_name": {"type": "string"},
                        "model_version": {"type": "string"},
                        "error": {"type": "string"},
                        "created_at": {"type": "string"},
                    },
                    "required": ["id", "input_type", "status", "created_at"],
                },
                "AIReviewListResponse": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/AIReviewDetail"},
                        }
                    },
                    "required": ["results"],
                },
                "AIReviewItem": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "episode_id": {"type": ["integer", "null"]},
                        "appointment_id": {"type": ["integer", "null"]},
                        "kind": {"type": "string"},
                        "payload_json": {"type": "object"},
                        "status": {"type": "string"},
                        "decided_at": {"type": ["string", "null"]},
                        "decided_by": {"type": ["integer", "null"]},
                        "decision_note": {"type": "string"},
                        "created_at": {"type": "string"},
                    },
                    "required": ["id", "kind", "status", "created_at"],
                },
                "AIReviewItemList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/AIReviewItem"},
                        }
                    },
                    "required": ["results"],
                },
                "AIReviewItemDecision": {
                    "type": "object",
                    "properties": {
                        "decision": {"type": "string"},
                        "note": {"type": "string"},
                    },
                    "required": ["decision"],
                },
                "AIReviewItemDecisionResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "status": {"type": "string"},
                        "decision_note": {"type": "string"},
                    },
                    "required": ["id", "status"],
                },
                "ConversationParticipant": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "email": {"type": ["string", "null"]},
                        "username": {"type": "string"},
                    },
                    "required": ["id", "username"],
                },
                "Conversation": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "episode_id": {"type": ["integer", "null"]},
                        "participants": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ConversationParticipant"},
                        },
                        "created_at": {"type": "string"},
                    },
                    "required": ["id", "participants", "created_at"],
                },
                "ConversationListResponse": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Conversation"},
                        }
                    },
                    "required": ["results"],
                },
                "ConversationCreateRequest": {
                    "type": "object",
                    "properties": {
                        "episode_id": {"type": "integer"},
                        "participants": {"type": "array", "items": {"type": "integer"}},
                    },
                },
                "Message": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "sender_id": {"type": ["integer", "null"]},
                        "body": {"type": "string"},
                        "created_at": {"type": "string"},
                        "read": {"type": "boolean"},
                    },
                    "required": ["id", "body", "created_at"],
                },
                "ConversationDetailResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "episode_id": {"type": ["integer", "null"]},
                        "participants": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ConversationParticipant"},
                        },
                        "messages": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Message"},
                        },
                    },
                    "required": ["id", "participants", "messages"],
                },
                "MessageCreateRequest": {
                    "type": "object",
                    "properties": {"body": {"type": "string"}},
                    "required": ["body"],
                },
                "MessageReadResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "read_at": {"type": "string"},
                    },
                    "required": ["id", "read_at"],
                },
                "Notification": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "kind": {"type": "string"},
                        "title": {"type": "string"},
                        "body": {"type": "string"},
                        "url": {"type": "string"},
                        "unread": {"type": "boolean"},
                        "read_at": {"type": ["string", "null"]},
                        "created_at": {"type": "string"},
                    },
                    "required": ["id", "title", "unread", "created_at"],
                },
                "NotificationList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Notification"},
                        },
                        "count": {"type": "integer"},
                        "page": {"type": "integer"},
                        "page_size": {"type": "integer"},
                    },
                    "required": ["results", "count", "page", "page_size"],
                },
                "NotificationReadResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "unread": {"type": "boolean"},
                        "read_at": {"type": ["string", "null"]},
                    },
                    "required": ["id", "unread"],
                },
                "ExportJob": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "kind": {"type": "string"},
                        "status": {"type": "string"},
                        "params": {"type": "object"},
                        "created_at": {"type": "string"},
                        "finished_at": {"type": ["string", "null"]},
                        "artifact_path": {"type": "string"},
                    },
                    "required": ["id", "kind", "status", "created_at"],
                },
                "ExportJobList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ExportJob"},
                        }
                    },
                    "required": ["results"],
                },
                "ExportJobRequest": {
                    "type": "object",
                    "properties": {
                        "kind": {"type": "string"},
                        "last_days": {"type": "integer"},
                    },
                    "required": ["kind"],
                },
                "Episode": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "status": {"type": "string"},
                        "created_at": {"type": "string"},
                        "updated_at": {"type": "string"},
                        "assigned_to": {"type": ["integer", "null"]},
                        "created_by": {"type": ["integer", "null"]},
                        "patient_id": {"type": ["integer", "null"]},
                    },
                    "required": ["id", "title", "status", "created_at", "updated_at"],
                },
                "EpisodeList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Episode"},
                        },
                        "count": {"type": "integer"},
                        "page": {"type": "integer"},
                        "page_size": {"type": "integer"},
                    },
                    "required": ["results", "count", "page", "page_size"],
                },
                "EpisodeEvent": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "event_type": {"type": "string"},
                        "from_state": {"type": "string"},
                        "to_state": {"type": "string"},
                        "from_status": {"type": "string"},
                        "to_status": {"type": "string"},
                        "note": {"type": "string"},
                        "payload_json": {"type": "object"},
                        "created_by": {"type": ["integer", "null"]},
                        "created_at": {"type": "string"},
                    },
                    "required": ["id", "event_type", "created_at"],
                },
                "EpisodeTimelineResponse": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/EpisodeEvent"},
                        },
                        "count": {"type": "integer"},
                        "page": {"type": "integer"},
                        "page_size": {"type": "integer"},
                    },
                    "required": ["results", "count", "page", "page_size"],
                },
                "EpisodeCreateRequest": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "patient_id": {"type": "integer"},
                        "assigned_to_id": {"type": "integer"},
                    },
                    "required": ["title"],
                },
                "EpisodeTransitionRequest": {
                    "type": "object",
                    "properties": {
                        "to_state": {"type": "string"},
                        "to_status": {"type": "string"},
                        "note": {"type": "string"},
                        "payload_json": {"type": "object"},
                    },
                    "required": ["to_state"],
                },
                "EpisodeTransitionResponse": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}, "status": {"type": "string"}},
                    "required": ["id", "status"],
                },
                "WorkItem": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "episode_id": {"type": ["integer", "null"]},
                        "kind": {"type": "string"},
                        "status": {"type": "string"},
                        "assigned_to": {"type": ["integer", "null"]},
                        "due_at": {"type": ["string", "null"]},
                        "sla_breach_at": {"type": ["string", "null"]},
                        "created_by": {"type": ["integer", "null"]},
                        "created_at": {"type": "string"},
                        "completed_at": {"type": ["string", "null"]},
                        "sla_breached": {"type": "boolean"},
                    },
                    "required": ["id", "kind", "status", "created_at", "sla_breached"],
                },
                "WorkItemListResponse": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/WorkItem"},
                        },
                        "count": {"type": "integer"},
                        "page": {"type": "integer"},
                        "page_size": {"type": "integer"},
                    },
                    "required": ["results", "count", "page", "page_size"],
                },
                "WorkItemAssignRequest": {
                    "type": "object",
                    "properties": {"assigned_to_id": {"type": "integer"}},
                },
                "WorkItemAssignResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "status": {"type": "string"},
                        "assigned_to": {"type": ["integer", "null"]},
                    },
                    "required": ["id", "status", "assigned_to"],
                },
                "WorkItemCompleteResponse": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}, "status": {"type": "string"}},
                    "required": ["id", "status"],
                },
                "Appointment": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "patient_id": {"type": ["integer", "null"]},
                        "episode_id": {"type": ["integer", "null"]},
                        "scheduled_at": {"type": "string"},
                        "duration_minutes": {"type": "integer"},
                        "location": {"type": "string"},
                        "status": {"type": "string"},
                        "notes": {"type": "string"},
                        "created_by": {"type": ["integer", "null"]},
                        "created_at": {"type": "string"},
                        "updated_at": {"type": "string"},
                    },
                    "required": ["id", "scheduled_at", "status", "created_at", "updated_at"],
                },
                "AppointmentListResponse": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Appointment"},
                        },
                        "count": {"type": "integer"},
                        "page": {"type": "integer"},
                        "page_size": {"type": "integer"},
                    },
                    "required": ["results", "count", "page", "page_size"],
                },
                "AppointmentCreateRequest": {
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "integer"},
                        "episode_id": {"type": "integer"},
                        "scheduled_at": {"type": "string"},
                        "duration_minutes": {"type": "integer"},
                        "location": {"type": "string"},
                        "status": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                    "required": ["scheduled_at"],
                },
                "AppointmentTransitionRequest": {
                    "type": "object",
                    "properties": {"to_state": {"type": "string"}, "to_status": {"type": "string"}},
                    "required": ["to_state"],
                },
                "AppointmentTransitionResponse": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}, "status": {"type": "string"}},
                    "required": ["id", "status"],
                },
                "Task": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "episode_id": {"type": ["integer", "null"]},
                        "work_item_id": {"type": ["integer", "null"]},
                        "title": {"type": "string"},
                        "status": {"type": "string"},
                        "priority": {"type": "string"},
                        "due_at": {"type": ["string", "null"]},
                        "assigned_to": {"type": ["integer", "null"]},
                        "created_by": {"type": ["integer", "null"]},
                        "created_at": {"type": "string"},
                        "completed_at": {"type": ["string", "null"]},
                    },
                    "required": ["id", "title", "status", "priority", "created_at"],
                },
                "TaskListResponse": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Task"},
                        },
                        "count": {"type": "integer"},
                        "page": {"type": "integer"},
                        "page_size": {"type": "integer"},
                    },
                    "required": ["results", "count", "page", "page_size"],
                },
                "TaskCreateRequest": {
                    "type": "object",
                    "properties": {
                        "episode_id": {"type": "integer"},
                        "work_item_id": {"type": "integer"},
                        "title": {"type": "string"},
                        "status": {"type": "string"},
                        "priority": {"type": "string"},
                        "due_at": {"type": "string"},
                    },
                    "required": ["title"],
                },
                "TaskAssignRequest": {
                    "type": "object",
                    "properties": {"assigned_to_id": {"type": "integer"}},
                },
                "TaskAssignResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "status": {"type": "string"},
                        "assigned_to": {"type": ["integer", "null"]},
                    },
                    "required": ["id", "status", "assigned_to"],
                },
                "TaskCompleteResponse": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}, "status": {"type": "string"}},
                    "required": ["id", "status"],
                },
                "Patient": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "given_name": {"type": "string"},
                        "family_name": {"type": "string"},
                        "date_of_birth": {"type": ["string", "null"]},
                        "nhs_number": {"type": ["string", "null"]},
                        "phone": {"type": "string"},
                        "email": {"type": "string"},
                        "address_line1": {"type": "string"},
                        "address_line2": {"type": "string"},
                        "city": {"type": "string"},
                        "region": {"type": "string"},
                        "postal_code": {"type": "string"},
                        "country": {"type": "string"},
                        "restricted": {"type": "boolean"},
                        "identifiers": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/PatientIdentifier"},
                        },
                        "addresses": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/PatientAddress"},
                        },
                        "contacts": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/PatientContactMethod"},
                        },
                        "created_at": {"type": "string"},
                        "updated_at": {"type": "string"},
                    },
                    "required": ["id", "given_name", "family_name", "created_at", "updated_at"],
                },
                "PatientList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Patient"},
                        },
                        "count": {"type": "integer"},
                        "page": {"type": "integer"},
                        "page_size": {"type": "integer"},
                    },
                    "required": ["results", "count", "page", "page_size"],
                },
                "PatientCreateRequest": {
                    "type": "object",
                    "properties": {
                        "given_name": {"type": "string"},
                        "family_name": {"type": "string"},
                        "date_of_birth": {"type": "string"},
                        "nhs_number": {"type": "string"},
                        "phone": {"type": "string"},
                        "email": {"type": "string"},
                        "address_line1": {"type": "string"},
                        "address_line2": {"type": "string"},
                        "city": {"type": "string"},
                        "region": {"type": "string"},
                        "postal_code": {"type": "string"},
                        "country": {"type": "string"},
                        "restricted": {"type": "boolean"},
                        "identifiers": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/PatientIdentifierInput"},
                        },
                        "addresses": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/PatientAddressInput"},
                        },
                        "contacts": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/PatientContactMethodInput"},
                        },
                    },
                    "required": ["given_name", "family_name"],
                },
                "PatientUpdateRequest": {
                    "type": "object",
                    "properties": {
                        "given_name": {"type": "string"},
                        "family_name": {"type": "string"},
                        "date_of_birth": {"type": "string"},
                        "nhs_number": {"type": "string"},
                        "phone": {"type": "string"},
                        "email": {"type": "string"},
                        "address_line1": {"type": "string"},
                        "address_line2": {"type": "string"},
                        "city": {"type": "string"},
                        "region": {"type": "string"},
                        "postal_code": {"type": "string"},
                        "country": {"type": "string"},
                        "restricted": {"type": "boolean"},
                        "identifiers": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/PatientIdentifierInput"},
                        },
                        "addresses": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/PatientAddressInput"},
                        },
                        "contacts": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/PatientContactMethodInput"},
                        },
                    },
                },
                "PatientIdentifier": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "kind": {"type": "string"},
                        "value": {"type": "string"},
                        "system": {"type": "string"},
                        "is_primary": {"type": "boolean"},
                    },
                    "required": ["id", "kind", "value"],
                },
                "PatientIdentifierInput": {
                    "type": "object",
                    "properties": {
                        "kind": {"type": "string"},
                        "value": {"type": "string"},
                        "system": {"type": "string"},
                        "is_primary": {"type": "boolean"},
                    },
                    "required": ["kind", "value"],
                },
                "PatientAddress": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "address_type": {"type": "string"},
                        "line1": {"type": "string"},
                        "line2": {"type": "string"},
                        "city": {"type": "string"},
                        "region": {"type": "string"},
                        "postal_code": {"type": "string"},
                        "country": {"type": "string"},
                        "is_primary": {"type": "boolean"},
                    },
                    "required": ["id", "line1"],
                },
                "PatientAddressInput": {
                    "type": "object",
                    "properties": {
                        "address_type": {"type": "string"},
                        "line1": {"type": "string"},
                        "line2": {"type": "string"},
                        "city": {"type": "string"},
                        "region": {"type": "string"},
                        "postal_code": {"type": "string"},
                        "country": {"type": "string"},
                        "is_primary": {"type": "boolean"},
                    },
                    "required": ["line1"],
                },
                "PatientContactMethod": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "kind": {"type": "string"},
                        "value": {"type": "string"},
                        "notes": {"type": "string"},
                        "is_primary": {"type": "boolean"},
                    },
                    "required": ["id", "kind", "value"],
                },
                "PatientContactMethodInput": {
                    "type": "object",
                    "properties": {
                        "kind": {"type": "string"},
                        "value": {"type": "string"},
                        "notes": {"type": "string"},
                        "is_primary": {"type": "boolean"},
                    },
                    "required": ["kind", "value"],
                },
                "PatientEpisodesResponse": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/PatientEpisodeSummary"},
                        }
                    },
                    "required": ["results"],
                },
                "PatientEpisodeSummary": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "title": {"type": "string"},
                        "status": {"type": "string"},
                        "created_at": {"type": "string"},
                        "updated_at": {"type": "string"},
                    },
                    "required": ["id", "title", "status", "created_at", "updated_at"],
                },
                "CareCircleMember": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "person_name": {"type": "string"},
                        "relationship": {"type": "string"},
                        "contact": {"type": "string"},
                        "notes": {"type": "string"},
                        "created_at": {"type": "string"},
                    },
                    "required": ["id", "person_name", "relationship", "created_at"],
                },
                "CareCircleMemberCreateRequest": {
                    "type": "object",
                    "properties": {
                        "person_name": {"type": "string"},
                        "relationship": {"type": "string"},
                        "contact": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                    "required": ["person_name", "relationship"],
                },
                "CareCircleMemberUpdateRequest": {
                    "type": "object",
                    "properties": {
                        "person_name": {"type": "string"},
                        "relationship": {"type": "string"},
                        "contact": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                },
                "CareCircleListResponse": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/CareCircleMember"},
                        }
                    },
                    "required": ["results"],
                },
                "PatientConsent": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "scope": {"type": "string"},
                        "lawful_basis": {"type": "string"},
                        "granted_by": {"type": "string"},
                        "expires_at": {"type": ["string", "null"]},
                        "granted": {"type": "boolean"},
                        "revoked_at": {"type": ["string", "null"]},
                        "policy_version": {"type": "string"},
                        "channel": {"type": "string"},
                        "recorded_at": {"type": "string"},
                    },
                    "required": ["id", "scope", "lawful_basis", "granted_by", "granted", "recorded_at"],
                },
                "PatientConsentCreateRequest": {
                    "type": "object",
                    "properties": {
                        "scope": {"type": "string"},
                        "lawful_basis": {"type": "string"},
                        "granted_by": {"type": "string"},
                        "expires_at": {"type": "string"},
                        "policy_version": {"type": "string"},
                        "channel": {"type": "string"},
                        "metadata": {"type": "object"},
                    },
                    "required": ["scope", "lawful_basis", "granted_by"],
                },
                "PatientConsentListResponse": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/PatientConsent"},
                        }
                    },
                    "required": ["results"],
                },
                "PatientMergeRequest": {
                    "type": "object",
                    "properties": {"source_id": {"type": "integer"}},
                    "required": ["source_id"],
                },
                "PatientMergeResponse": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}, "merged_source_id": {"type": "integer"}},
                    "required": ["id", "merged_source_id"],
                },
                "EvidenceItem": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "title": {"type": "string"},
                        "kind": {"type": "string"},
                        "episode_id": {"type": ["integer", "null"]},
                        "patient_id": {"type": ["integer", "null"]},
                        "file_name": {"type": "string"},
                        "content_type": {"type": "string"},
                        "size_bytes": {"type": "integer"},
                        "storage_key": {"type": "string"},
                        "sha256": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "retention_class": {"type": "string"},
                        "retention_until": {"type": ["string", "null"]},
                        "created_at": {"type": "string"},
                    },
                    "required": [
                        "id",
                        "title",
                        "kind",
                        "file_name",
                        "size_bytes",
                        "sha256",
                        "tags",
                        "created_at",
                    ],
                },
                "EvidenceEvent": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "event_type": {"type": "string"},
                        "payload_json": {"type": "object"},
                        "created_by": {"type": ["integer", "null"]},
                        "created_at": {"type": "string"},
                    },
                    "required": ["id", "event_type", "created_at"],
                },
                "EvidenceEventList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/EvidenceEvent"},
                        },
                        "count": {"type": "integer"},
                        "page": {"type": "integer"},
                        "page_size": {"type": "integer"},
                    },
                    "required": ["results", "count", "page", "page_size"],
                },
                "EvidenceListResponse": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/EvidenceItem"},
                        },
                        "count": {"type": "integer"},
                        "page": {"type": "integer"},
                        "page_size": {"type": "integer"},
                    },
                    "required": ["results", "count", "page", "page_size"],
                },
                "EvidenceCreateRequest": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "kind": {"type": "string"},
                        "episode_id": {"type": "string"},
                        "patient_id": {"type": "string"},
                        "tags": {"type": "string"},
                        "retention_class": {"type": "string"},
                        "retention_until": {"type": "string"},
                        "file": {"type": "string", "format": "binary"},
                    },
                    "required": ["kind", "file"],
                },
                "EvidenceLinkRequest": {
                    "type": "object",
                    "properties": {
                        "episode_id": {"type": "integer"},
                        "patient_id": {"type": "integer"},
                    },
                },
                "EvidenceLinkResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "episode_id": {"type": ["integer", "null"]},
                        "patient_id": {"type": ["integer", "null"]},
                    },
                    "required": ["id", "episode_id", "patient_id"],
                },
                "EvidenceTagRequest": {
                    "type": "object",
                    "properties": {"tags": {"type": "array", "items": {"type": "string"}}},
                    "required": ["tags"],
                },
                "EvidenceTagResponse": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["id", "tags"],
                },
                "EvidenceBundle": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "episode_id": {"type": "integer"},
                        "created_at": {"type": "string"},
                        "artifact_path": {"type": ["string", "null"]},
                        "manifest": {"type": "object"},
                    },
                    "required": ["id", "episode_id", "created_at"],
                },
                "EvidenceBundleList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/EvidenceBundle"},
                        }
                    },
                    "required": ["results"],
                },
                "ReportJob": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "report_type": {"type": "string"},
                        "status": {"type": "string"},
                        "interval_days": {"type": "integer"},
                        "next_run_at": {"type": ["string", "null"]},
                        "last_run_at": {"type": ["string", "null"]},
                        "artifact_path": {"type": ["string", "null"]},
                    },
                    "required": ["id", "name", "report_type", "status", "interval_days"],
                },
                "ReportJobList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ReportJob"},
                        }
                    },
                    "required": ["results"],
                },
                "ReportJobCreateRequest": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "report_type": {"type": "string"},
                        "interval_days": {"type": "integer"},
                        "next_run_at": {"type": "string"},
                        "params": {"type": "object"},
                    },
                    "required": ["name", "report_type"],
                },
                "SubmissionRecord": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "episode_id": {"type": ["integer", "null"]},
                        "due_date": {"type": "string"},
                        "submitted_at": {"type": ["string", "null"]},
                        "status": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                    "required": ["id", "due_date", "status"],
                },
                "SubmissionRecordList": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/SubmissionRecord"},
                        }
                    },
                    "required": ["results"],
                },
                "SubmissionRecordCreateRequest": {
                    "type": "object",
                    "properties": {
                        "episode_id": {"type": "integer"},
                        "due_date": {"type": "string"},
                        "submitted_at": {"type": "string"},
                        "status": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                    "required": ["due_date"],
                },
            },
            "securitySchemes": {
                "cookieAuth": {"type": "apiKey", "in": "cookie", "name": "sessionid"}
            },
        },
    }
