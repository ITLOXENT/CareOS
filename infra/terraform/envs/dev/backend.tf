terraform {
  backend "s3" {
    bucket         = "careos-terraform-state"
    key            = "careos/dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "careos-terraform-locks"
    encrypt        = true
  }
}
