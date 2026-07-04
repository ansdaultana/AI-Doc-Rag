FROM node:20-alpine AS build
# "start from an image that already has Node.js installed"
# alpine = a tiny Linux distro, keeps the image small
# AS build = name this stage "build" (used later in the second stage)

WORKDIR /app
# "all commands from now on run inside /app"

COPY package*.json ./
# copy ONLY package.json (and package-lock.json if it exists)
# into the container's current folder (/app)

RUN npm install
# install all dependencies listed in package.json
# CACHED as long as package.json hasn't changed

COPY . .
# NOW copy everything else (your actual React source code)

RUN npm run build
# run Vite's build command → produces a "dist/" folder
# containing plain HTML, CSS, JS — no React dev tools, just
# the finished website ready to be served

# ---- second stage ----
FROM nginx:alpine
# start fresh from nginx (a web server) — we don't need Node anymore

COPY --from=build /app/dist /usr/share/nginx/html
# copy ONLY the built "dist/" folder from the first stage
# into nginx's web root — the place nginx serves files from
# everything else (node_modules, source code) gets left behind,
# keeping this final container small

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
# start nginx and keep it running in the foreground