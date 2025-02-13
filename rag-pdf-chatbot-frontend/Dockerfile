# Use official Node.js image
FROM node:18

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies first
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the frontend files
COPY . .

# Expose port for frontend
EXPOSE 3000

# Start the React app
CMD ["npm", "start"]
