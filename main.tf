provider "aws" {
  region = "sa-east-1" # Setando região de São Paulo
}

#Pasta com criação das roles
module "roles" {
  source = "./roles"
}
