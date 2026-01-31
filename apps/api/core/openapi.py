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
                }
            },
            "/audit-events/": {
                "get": {
                    "summary": "Audit events",
                    "security": [{"cookieAuth": []}],
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
        },
        "components": {
            "schemas": {
                "HealthResponse": {
                    "type": "object",
                    "properties": {"status": {"type": "string"}},
                    "required": ["status"],
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
                "AuditEvent": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "action": {"type": "string"},
                        "target_type": {"type": "string"},
                        "target_id": {"type": "string"},
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
                        }
                    },
                    "required": ["results"],
                },
            },
            "securitySchemes": {
                "cookieAuth": {"type": "apiKey", "in": "cookie", "name": "sessionid"}
            },
        },
    }
