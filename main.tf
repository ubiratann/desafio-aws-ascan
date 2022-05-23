provider "aws" {
  region = "sa-east-1" # Setando região de São Paulo
}

#Módulo com definição das roles
module "roles" {
  source = "./roles"
}

# Módulo com definição do bucket usado
module "buckets" {
  source = "./buckets"
}
