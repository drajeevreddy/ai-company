# Docker + Apache + SELinux Deployment Recipe

## Context
- Host: Fedora, SELinux Enforcing
- App: PHP with CSV storage, depends on `.htaccess` for security
- No host PHP — all PHP runs in container

## Dockerfile
```dockerfile
FROM php:8.3-apache
RUN a2enmod rewrite headers
# PHP hardening
RUN echo "display_errors=Off" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "expose_php=Off" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.use_strict_mode=1" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.cookie_httponly=1" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.cookie_secure=1" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.gc_maxlifetime=1440" >> $PHP_INI_DIR/conf.d/hardening.ini
# Zip extension for admin backups
RUN apt-get update && apt-get install -y --no-install-recommends libzip-dev \
    && docker-php-ext-install zip \
    && rm -rf /var/lib/apt/lists/*
```

## Run Command
```bash
docker build -t appointment-php:hardened /path/to/dockerfile
docker run -d --name appointment \
  --restart unless-stopped \
  -p 8080:80 \
  -v /host/path:/var/www/html:z \
  appointment-php:hardened
```

## Key Points
- `:z` flag on bind mount — relabels for SELinux (required on Fedora Enforcing)
- `a2enmod rewrite headers` — enables `.htaccess` processing
- No host PHP — lint via `docker exec appointment php -l /var/www/html/file.php`
- Container runs as `www-data` but files owned by host UID 1000 (see ownership model)

## Troubleshooting
| Symptom | Cause | Fix |
|---------|-------|-----|
| 403 on bind mount | SELinux blocks | Add `:z` flag |
| 500 on install.php | Missing mod_rewrite | `a2enmod rewrite` in Dockerfile |
| Headers already sent | POST/export after HTML | Move handlers before `header.php` |
| ZipArchive not found | Missing extension | Install `libzip-dev` + `docker-php-ext-install zip` |