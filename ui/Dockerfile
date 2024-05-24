# Use the official Node.js image
FROM node:14

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json ./
RUN npm install

# Copy the rest of the application code
COPY ./src ./src
COPY ./public ./public

# Start the React development server
CMD ["npm", "start"]

