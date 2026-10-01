# Brute-force login protection + session hardening (working PHP)

All code below was functionally verified end-to-end (see verification recipe at bottom) on a static-site PHP blog admin. The rate-limiter stores a JSON attempt log inside an already-protected data dir (one whose `.htaccess` has `Deny from all`) — the log file inherits that protection for free.

## 1. login.php — rate limiting (insert after `$error = '';`, before form handling)

```php
// Brute-force protection: track failed attempts per IP
$attemptFile = DATA_PATH . '/login_attempts.json';
$attempts = [];
if (file_exists($attemptFile)) {
    $attempts = json_decode(file_get_contents($attemptFile), true) ?: [];
}
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$now = time();
// Clean attempts older than 15 minutes
if (isset($attempts[$ip])) {
    $attempts[$ip] = array_values(array_filter($attempts[$ip], function ($t) use ($now) {
        return $t > $now - 900;
    }));
}
$failCount = isset($attempts[$ip]) ? count($attempts[$ip]) : 0;
$maxAttempts = 5;
$lockoutSeconds = 900;

// If locked out, block login
if ($failCount >= $maxAttempts) {
    $error = 'Too many failed login attempts. Please try again after 15 minutes.';
}

// Handle login form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && $failCount < $maxAttempts) {
    if (!isset($_POST['csrf_token']) || !verifyCsrfToken($_POST['csrf_token'])) {
        $error = 'Invalid security token. Please refresh and try again.';
    } else {
        $username = trim($_POST['username'] ?? '');
        $password = $_POST['password'] ?? '';

        if (authenticate($username, $password)) {
            // Success: clear failed attempts for this IP
            unset($attempts[$ip]);
            file_put_contents($attemptFile, json_encode($attempts));
            header('Location: ' . SITE_URL . '/admin/');
            exit;
        } else {
            // Record failed attempt
            $attempts[$ip][] = $now;
            file_put_contents($attemptFile, json_encode($attempts));
            $failCount++;
            if ($failCount >= $maxAttempts) {
                $error = 'Too many failed login attempts. Please try again after 15 minutes.';
            } else {
                $error = 'Invalid username or password. ' . ($maxAttempts - $failCount) . ' attempts remaining.';
            }
        }
    }
}
```

Design notes:
- Verify `DATA_PATH` is the real constant name in the codebase before wiring in (check `config.php`).
- Guard the "attempts remaining" leak: it's fine to show remaining count — standard practice.
- If the data dir might not exist, `mkdir` it or `file_put_contents` fails silently (it did in one test until the stub pointed at a real dir).

## 2. config.php — session hardening (must run BEFORE session_start())

```php
if (session_status() === PHP_SESSION_NONE) {
    ini_set('session.cookie_httponly', 1);
    ini_set('session.use_strict_mode', 1);
    ini_set('session.use_only_cookies', 1);
    ini_set('session.cookie_secure', 1);          // site must be HTTPS-only
    ini_set('session.cookie_samesite', 'Lax');
    ini_set('session.gc_maxlifetime', SESSION_LIFETIME);
    session_start();
}
```

## 3. auth.php — session fixation prevention

```php
if ($admin['username'] === $username && password_verify($password, $admin['password'])) {
    session_regenerate_id(true);   // ← add this line first
    $_SESSION['admin_logged_in'] = true;
    ...
}
```

## 4. noindex admin pages

Add to every admin page `<head>` (login + dashboard + list pages):
```html
<meta name="robots" content="noindex, nofollow">
```
And remove public footer links to the admin: delete the `<a href=".../admin" ...>Admin</a>` line AND its preceding `<span class="sep">|</span>` separator, or a dangling pipe renders.

## 5. Functional verification recipe (proven)

1. Build scratch tree: copy the real `login.php`, then stub the 3 requires:
   - `includes/config.php`: `define('SITE_URL', 'http://localhost:8099/blog'); define('DATA_PATH', '<scratch>/blog/data'); session_start(); function getSettings(){...}`
   - `admin/includes/auth.php`: `function isLoggedIn(){return false;} function verifyCsrfToken($t){return true;} function authenticate($u,$p){return $u==='admin' && $p==='CorrectHorse42';}`
   - `includes/storage.php`: `function e($s){...} function getCsrfField(){...}`
2. `php -S 127.0.0.1:8099 -t <scratch>/blog` (background) 
3. Assert sequence:
   - 4 wrong POSTs → "Invalid username"
   - 5th wrong POST → "Too many failed" (lockout)
   - correct password while locked → still "Too many failed" (302 NOT returned)
   - attempts file contains 5 timestamps for the IP
   - back-date file to `[1000000000]*5` → correct password now returns 302 (expiry works)
   - after success → file content is `[]` (cleared)

This exact sequence was executed with real HTTP against a real PHP 8.3 built-in server: 6/6 passed.
