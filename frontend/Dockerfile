# pull official base image
FROM node:14-alpine

# set working directory
WORKDIR /app

# Copy built files to serve
COPY build /app

# Install serve
RUN npm install -g serve

# start app
CMD ["serve", "-s", "/app", "-l", "3000"]
