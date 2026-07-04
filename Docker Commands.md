# Docker Commands — Quick Reference

## Build & Run
```bash
docker compose up --build                   # rebuild everything + start
docker compose up --build backend           # rebuild + start only backend
docker compose up -d                        # start everything in background
docker compose up -d --build backend        # rebuild backend, run in background
docker compose start frontend               # start already-built frontend (no rebuild)
docker compose restart backend              # restart without rebuilding
```

## Stop
```bash
docker compose down                         # stop and remove containers
docker compose down -v                      # stop + delete volumes (wipes postgres!)
docker compose stop                         # stop containers but keep them
```

## Logs
```bash
docker compose logs backend                 # see backend logs
docker compose logs -f backend              # follow logs live
docker compose logs -f                      # follow all containers live
```

## Debug Inside a Container
```bash
docker compose exec backend bash            # open shell inside backend
docker compose exec backend python -c "import sqlalchemy; print('ok')"
```

## Status
```bash
docker compose ps                           # running containers + status
docker images                               # all built images
docker system df                            # disk usage
```

## Cleanup
```bash
docker system prune                         # remove unused images/containers
docker system prune -a                      # remove everything not running
```