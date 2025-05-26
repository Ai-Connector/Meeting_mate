# 1. Use an appropriate Node.js base image
FROM node:18-alpine AS builder

# 2. Set the working directory
WORKDIR /usr/src/app

# Set NODE_ENV to production for build stage as well, good practice
ENV NODE_ENV production

# 3. Copy package.json and package-lock.json
# (npm ci will also use package-lock.json if available)
COPY package.json ./
COPY package-lock.json* ./
# If you have an npm-shrinkwrap.json, copy it too:
# COPY npm-shrinkwrap.json ./

# 4. Install dependencies
# Using npm ci for cleaner, more reliable builds from package-lock
RUN npm ci

# 5. Copy the rest of the application code
# Copy all files from the frontend directory in the host to the current directory in the image
COPY . .

# 6. Build the Next.js application
# This will also use the generate-grpc script if it's part of the build process in package.json (it's not by default)
# Ensure that any necessary generated files (like gRPC stubs) are present before this step.
# The previous steps copied the 'generated' and 'protos' directories.
RUN npm run build

# --- Production Stage ---
FROM node:18-alpine

WORKDIR /usr/src/app

# 7. Set the NODE_ENV to production
ENV NODE_ENV production

# Copy built assets from the builder stage
COPY --from=builder /usr/src/app/.next ./.next
COPY --from=builder /usr/src/app/node_modules ./node_modules
COPY --from=builder /usr/src/app/package.json ./package.json
# Copy next.config.js and public folder if they are needed for production runtime
COPY --from=builder /usr/src/app/next.config.ts ./next.config.ts
COPY --from=builder /usr/src/app/public ./public

# 8. Expose the port Next.js runs on
EXPOSE 3000

# 9. Define the command to start the Next.js application
# npm start should execute `next start` as per typical Next.js package.json scripts
CMD ["npm", "start"]
