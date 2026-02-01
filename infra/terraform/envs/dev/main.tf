locals {
  name = "careos-dev"
  tags = {
    Environment = "dev"
    Project     = "CareOS"
    ManagedBy   = "terraform"
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = local.tags
  }
}

module "network" {
  source               = "../../modules/network"
  name                 = local.name
  cidr_block           = var.vpc_cidr
  public_subnet_count  = 2
  private_subnet_count = 2
  enable_nat           = var.enable_nat
}

module "security" {
  source   = "../../modules/security"
  name     = local.name
  vpc_id   = module.network.vpc_id
  app_port = var.app_port
  db_port  = var.db_port
}

module "db" {
  source                 = "../../modules/db"
  name                   = local.name
  subnet_ids             = module.network.private_subnet_ids
  vpc_security_group_ids = [module.security.rds_security_group_id]
}

module "compute" {
  source                = "../../modules/compute"
  name                  = local.name
  vpc_id                = module.network.vpc_id
  public_subnet_ids     = module.network.public_subnet_ids
  private_subnet_ids    = module.network.private_subnet_ids
  alb_security_group_id = module.security.alb_security_group_id
  ecs_security_group_id = module.security.ecs_security_group_id
  app_port              = var.app_port
  desired_count         = var.desired_count
  domain_name           = var.domain_name
  sentry_dsn            = var.sentry_dsn
  sentry_environment    = var.sentry_environment
  sentry_release        = var.sentry_release
  sentry_traces_sample_rate = var.sentry_traces_sample_rate
  sentry_send_default_pii   = var.sentry_send_default_pii
}

module "observability" {
  source           = "../../modules/observability"
  name             = local.name
  db_instance_id   = module.db.db_instance_id
  ecs_cluster_name = module.compute.cluster_name
  ecs_service_name = module.compute.service_name
}
