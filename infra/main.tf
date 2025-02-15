######################################################
# AWS Provider
######################################################
provider "aws" {
  region = var.aws_region
}

######################################################
# VPC
######################################################
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "main-vpc"
  }
}

######################################################
# Internet Gateway
######################################################
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "main-igw"
  }
}

######################################################
# Public Subnet
######################################################
resource "aws_subnet" "main" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true  # <-- Enable auto-assign public IP

  tags = {
    Name = "main-public-subnet"
  }
}

######################################################
# Route Table + Association for Public Subnet
######################################################
resource "aws_route_table" "main" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "main-public-rt"
  }
}

resource "aws_route_table_association" "main_public_association" {
  subnet_id      = aws_subnet.main.id
  route_table_id = aws_route_table.main.id
}

######################################################
# Security Group
######################################################
resource "aws_security_group" "ec2_sg" {
  name        = "ec2-security-group"
  description = "Allow SSH and HTTP access"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # SSH from anywhere
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # HTTP from anywhere
  }

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # HTTP from anywhere
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]  # Allow all outbound
  }

  tags = {
    Name = "ec2-security-group"
  }
}

######################################################
# EC2 Instance
######################################################
resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = aws_subnet.main.id
  
  # Use Security Group IDs, not names, when you specify a subnet
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]

  # Associate a Public IP. This is optional if 'map_public_ip_on_launch' = true,
  # but explicitly setting it can be a good reminder of your intentions.
  associate_public_ip_address = true

  tags = {
    Name = "web-server"
  }
}

######################################################
# Outputs
######################################################
output "public_ip" {
  value = aws_instance.web.public_ip
}
