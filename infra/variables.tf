variable "aws_region" {
  description = "The AWS region to deploy resources"
  default     = "us-east-1"
}

variable "ami_id" {
  description = "The AMI ID for the EC2 instance"
  default     = "ami-0c02fb55956c7d316"  # Replace with your Amazon Linux 2023 AMI ID
}

variable "instance_type" {
  description = "The instance type for the EC2 instance"
  default     = "t2.large"
}