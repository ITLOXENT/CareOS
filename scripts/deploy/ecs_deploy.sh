#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${AWS_REGION:-}" || -z "${ECS_CLUSTER:-}" || -z "${ECS_SERVICE:-}" ]]; then
  echo "AWS_REGION, ECS_CLUSTER, and ECS_SERVICE must be set."
  exit 1
fi

echo "Deploying ${ECS_SERVICE} to cluster ${ECS_CLUSTER} in ${AWS_REGION}..."
aws ecs update-service \
  --region "${AWS_REGION}" \
  --cluster "${ECS_CLUSTER}" \
  --service "${ECS_SERVICE}" \
  --force-new-deployment

aws ecs wait services-stable \
  --region "${AWS_REGION}" \
  --cluster "${ECS_CLUSTER}" \
  --services "${ECS_SERVICE}"

echo "Deployment complete."
