terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}

# Resource 1: The Docker Image
resource "docker_image" "symptom_checker" {
  name         = "ai-symptom-checker:latest"
  keep_locally = true
}

# Resource 2: The Docker Container
resource "docker_container" "symptom_checker_container" {
  image = docker_image.symptom_checker.image_id
  name  = "ai-health-app"
  ports {
    internal = 8000
    external = 8000
  }
}
