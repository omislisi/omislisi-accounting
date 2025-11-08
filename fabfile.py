import os
import shutil
import subprocess
from fabric.api import env, local, puts, abort, cd, hide
from fabric.colors import green, yellow
from fabric.contrib.files import exists, upload_template
from fabric.operations import put, sudo, run

env.forward_agent = True
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
USER = "omislisi"

ENVIRONMENTS = {
    "production": {
        "domain_name": "fin.omisli.si",
        "web_directory": "/home/omislisi/fin.omisli.si",
        "secure": True,
    },
}


def web(environment="production"):
    """Connect to production server (web.omisli.si)"""
    env.hosts = ["web.omisli.si"]
    env.user = "omislisi"
    config_environment(environment)


def config_environment(environment_name):
    """Set environment variables"""
    if environment_name not in ENVIRONMENTS:
        abort("Environment %s not found in ENVIRONMENTS" % environment_name)

    environment = ENVIRONMENTS[environment_name]
    env.environment_name = environment_name
    env.domain_name = environment["domain_name"]
    env.web_directory = environment["web_directory"]
    env.secure = environment["secure"]


def decrypt_settings(source_file, target_file):
    """Decrypts a SOPS-encrypted settings file"""
    import os

    # Ensure GPG_TTY is set if we have a TTY
    env = os.environ.copy()
    if 'GPG_TTY' not in env:
        # Try to inherit from current environment or set from tty command
        try:
            tty_result = subprocess.run(['tty'], capture_output=True, text=True, check=True)
            env['GPG_TTY'] = tty_result.stdout.strip()
        except:
            pass

    # Run SOPS decryption
    result = subprocess.run(
        ['sops', '-d', source_file],
        stdout=open(target_file, 'w'),
        stderr=subprocess.PIPE,
        env=env,
        check=True
    )

    # If decryption fails, the error will be raised above
    # The stderr will contain details about what went wrong


def encrypt_settings(source_file):
    """Encrypts a settings file using SOPS"""
    with hide('running', 'stdout'):
        os.execvp('sops', ['sops', '--encrypt', '--in-place', source_file])


def edit_settings(source_file):
    """Safely edits a SOPS-encrypted settings file"""
    with hide('running', 'stdout'):
        os.execvp('sops', ['sops', source_file, '-e code --wait'])


def sync_dashboard():
    """Sync locally generated dashboard to server web directory"""
    puts(green("Syncing dashboard to server..."))

    local_dashboard = os.path.join(ROOT_DIR, "dashboard")
    if not os.path.exists(local_dashboard):
        abort("Dashboard directory not found. Please run 'oa generate-dashboard --output-dir ./dashboard' first.")

    # Ensure web directory exists on server with proper permissions
    sudo("mkdir -p %s" % env.web_directory)
    sudo("mkdir -p %s/.well-known/acme-challenge" % env.web_directory)
    sudo("chown -R %s.%s %s" % (USER, USER, env.web_directory))
    # Set restrictive permissions: owner can read/write/execute, group and others can only read/execute
    sudo("chmod -R 755 %s" % env.web_directory)
    # Ensure .well-known directory is accessible for ACME challenges
    sudo("chmod 755 %s/.well-known" % env.web_directory)
    sudo("chmod 755 %s/.well-known/acme-challenge" % env.web_directory)

    # Upload dashboard files using rsync
    puts(green("Uploading dashboard files..."))
    local(
        "rsync -avz --delete %s/ %s@%s:%s/"
        % (local_dashboard, env.user, env.hosts[0], env.web_directory)
    )

    # Set proper permissions
    sudo("chown -R %s.%s %s" % (USER, USER, env.web_directory))
    sudo("chmod -R 755 %s" % env.web_directory)

    puts(green("Dashboard synced successfully!"))


def setup_htpasswd():
    """Decrypt and upload htpasswd file to server (same pattern as Django project)"""
    puts(green("Setting up HTTP Basic Auth..."))

    source_file = os.path.join(ROOT_DIR, "deploy", env.environment_name, "htpasswd")
    if not os.path.exists(source_file):
        abort("htpasswd file not found at %s. Please create it first." % source_file)

    target_file = "/etc/nginx/htpasswd-fin"
    temp_file = "/tmp/htpasswd_fin_%s" % os.getpid()

    try:
        # Decrypt the htpasswd file to temp file (same as Django project pattern)
        puts(green("Decrypting htpasswd file locally..."))
        decrypt_settings(source_file, temp_file)

        # Upload the decrypted file to server
        puts(green("Uploading htpasswd file to server..."))
        put(temp_file, target_file, use_sudo=True)

        # Set proper permissions (readable only by root and nginx user)
        sudo("chmod 640 %s" % target_file)
        sudo("chown root.www-data %s" % target_file)

        puts(green("HTTP Basic Auth configured successfully!"))
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)


def edit_htpasswd(environment="production"):
    """Edit encrypted htpasswd file using SOPS"""
    if not hasattr(env, 'environment_name'):
        env.environment_name = environment
    source_file = os.path.join(ROOT_DIR, "deploy", env.environment_name, "htpasswd")
    if not os.path.exists(source_file):
        puts(yellow("htpasswd file not found. Creating new encrypted file..."))
        # Create empty file first, then encrypt it
        with open(source_file, 'w') as f:
            f.write("")
        encrypt_settings(source_file)

    edit_settings(source_file)


def encrypt_htpasswd(environment="production"):
    """Encrypt htpasswd file using SOPS"""
    if not hasattr(env, 'environment_name'):
        env.environment_name = environment
    source_file = os.path.join(ROOT_DIR, "deploy", env.environment_name, "htpasswd")
    if not os.path.exists(source_file):
        abort("htpasswd file not found at %s" % source_file)

    encrypt_settings(source_file)
    puts(green("htpasswd file encrypted successfully!"))


def add_user(username, environment="production"):
    """Add user to htpasswd file (decrypt, add, re-encrypt)"""
    if not hasattr(env, 'environment_name'):
        env.environment_name = environment
    source_file = os.path.join(ROOT_DIR, "deploy", env.environment_name, "htpasswd")
    temp_file = "/tmp/htpasswd_temp_%s" % os.getpid()

    try:
        # Decrypt if encrypted, or use existing plaintext
        is_encrypted = False
        if os.path.exists(source_file):
            # Try to decrypt (will fail if not encrypted)
            try:
                decrypt_settings(source_file, temp_file)
                is_encrypted = True
            except:
                # File is not encrypted, copy it
                shutil.copy(source_file, temp_file)
                is_encrypted = False
        else:
            # Create new file
            with open(temp_file, 'w') as f:
                f.write("")
            is_encrypted = False

        # Add user using htpasswd command
        puts(green("Adding user %s..." % username))
        local("htpasswd %s %s" % (temp_file, username))

        # If it was encrypted, encrypt the temp file, then move it
        if is_encrypted:
            # Encrypt in place
            with hide('running', 'stdout'):
                subprocess.run(['sops', '--encrypt', '--in-place', temp_file], check=True)

        # Replace original file
        shutil.move(temp_file, source_file)

        puts(green("User %s added successfully!" % username))
    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise


def nginxconfig(secure=None):
    """Deploy nginx configuration template"""
    puts(green("Deploying nginx configuration..."))

    # Allow overriding secure flag
    if secure is None:
        secure = env.secure

    data = {
        "domain_name": env.domain_name,
        "web_directory": env.web_directory,
        "secure": secure,
    }

    upload_template(
        "nginx.conf",
        "/etc/nginx/sites-enabled/fin-omislisi.conf",
        context=data,
        use_sudo=True,
        backup=False,
        use_jinja=True,
        template_dir=os.path.join(ROOT_DIR, "deploy"),
        mode=0o0400,
    )

    puts(green("Nginx configuration deployed!"))


def nginxtest():
    """Test nginx configuration"""
    result = sudo("nginx -t", warn_only=True)
    if result.return_code == 0:
        puts(green("Nginx configuration is valid!"))
    else:
        puts(yellow("Nginx configuration has errors. Check the output above."))
    return result


def check_nginx_config():
    """Check the deployed nginx configuration"""
    puts(green("Checking nginx configuration on server..."))
    puts(yellow("auth_basic settings:"))
    run("grep -A5 'auth_basic' /etc/nginx/sites-enabled/fin-omislisi.conf")
    puts(yellow("\nACME challenge location:"))
    run("grep -A5 '/.well-known/acme-challenge' /etc/nginx/sites-enabled/fin-omislisi.conf")
    puts(yellow("\nOther configs matching fin.omisli.si:"))
    run("grep -r 'fin.omisli.si' /etc/nginx/sites-enabled/ 2>/dev/null || echo 'No other matches'")
    puts(yellow("\nChecking if web directory exists:"))
    run("ls -la %s/.well-known/acme-challenge/ 2>&1 || echo 'Directory does not exist'" % env.web_directory)
    puts(yellow("\nAll server blocks listening on port 80:"))
    run("grep -r 'listen.*80' /etc/nginx/sites-enabled/ | grep -v '#'")
    puts(yellow("\nDefault server blocks:"))
    run("grep -r 'default_server' /etc/nginx/sites-enabled/ | head -5")
    puts(yellow("\nChecking production-omislisi.conf server_name:"))
    run("grep -A2 'server_name' /etc/nginx/sites-enabled/production-omislisi.conf | head -10")
    puts(yellow("\nFull fin-omislisi.conf file (first 50 lines):"))
    run("head -50 /etc/nginx/sites-enabled/fin-omislisi.conf")
    puts(yellow("\nChecking if secure flag was set correctly:"))
    run("grep -c 'ssl_certificate' /etc/nginx/sites-enabled/fin-omislisi.conf || echo '0'")
    puts(yellow("\nRecent nginx error logs:"))
    run("tail -10 /var/log/nginx/error.log 2>/dev/null || echo 'No error log'")
    puts(yellow("\nChecking htpasswd file:"))
    run("test -f /etc/nginx/htpasswd-fin && echo 'htpasswd file exists' || echo 'htpasswd file MISSING'")


def prepare_acme_challenge():
    """Create directory for ACME challenge and test access"""
    puts(green("Preparing ACME challenge directory..."))
    sudo("mkdir -p %s/.well-known/acme-challenge" % env.web_directory)
    sudo("chown -R %s.%s %s" % (USER, USER, env.web_directory))
    sudo("chmod -R 755 %s" % env.web_directory)
    # Create a test file
    sudo("echo 'test' > %s/.well-known/acme-challenge/test.txt" % env.web_directory)
    sudo("chown %s.%s %s/.well-known/acme-challenge/test.txt" % (USER, USER, env.web_directory))
    puts(green("ACME challenge directory prepared!"))


def nginxstart():
    """Start nginx"""
    # Test config first - if it fails, try deploying without SSL
    test_result = nginxtest()
    if test_result.return_code != 0:
        puts(yellow("Config test failed. Redeploying without SSL..."))
        nginxconfig(secure=False)
        nginxtest()
    sudo("service nginx start")
    puts(green("Nginx started!"))


def nginxreload():
    """Reload nginx"""
    sudo("service nginx reload")
    puts(green("Nginx reloaded!"))


def nginxrestart():
    """Restart nginx"""
    sudo("service nginx restart")
    puts(green("Nginx restarted!"))


def setup_certbot():
    """Set up Let's Encrypt SSL certificate for subdomain using webroot (nginx stays running)"""
    puts(green("Setting up SSL certificate for %s..." % env.domain_name))
    # Try to update, but continue if it fails (non-critical)
    with hide('running', 'stdout', 'stderr'):
        try:
            sudo("apt-get update", warn_only=True)
        except:
            pass
    # Check if certbot is already installed
    with hide('running', 'stdout', 'stderr'):
        result = sudo("which certbot", warn_only=True)
        if result.return_code != 0:
            sudo("apt-get install -y certbot")

    # Ensure webroot directory exists for Let's Encrypt validation
    # Certbot needs to write challenge files here
    sudo("mkdir -p %s/.well-known/acme-challenge" % env.web_directory)
    sudo("chown -R %s.%s %s" % (USER, USER, env.web_directory))
    sudo("chmod -R 755 %s" % env.web_directory)

    # Use webroot mode - nginx stays running!
    # This requires nginx to serve /.well-known/acme-challenge from webroot
    puts(green("Using webroot mode - nginx will continue running during certificate setup"))

    # Use the newer account (option 1) by specifying account ID
    # Account: web.omisli.si@2020-06-21T20:45:41Z (72b6)
    result = sudo(
        "certbot certonly --webroot --webroot-path=%s --email primoz.verdnik@gmail.com --no-eff-email --agree-tos -d %s --non-interactive --account 72b6 2>&1"
        % (env.web_directory, env.domain_name),
        warn_only=True
    )

    if result.return_code != 0:
        # If account ID doesn't work, try with the full account identifier
        result_str = str(result) if hasattr(result, '__str__') else ''
        if "choose an account" in result_str.lower() or "Please choose" in result_str or "does not exist" in result_str:
            puts(yellow("Trying with full account identifier..."))
            result = sudo(
                "certbot certonly --webroot --webroot-path=%s --email primoz.verdnik@gmail.com --no-eff-email --agree-tos -d %s --non-interactive --account web.omisli.si@2020-06-21T20:45:41Z 2>&1"
                % (env.web_directory, env.domain_name),
                warn_only=True
            )

            if result.return_code != 0:
                puts(yellow("Certificate setup requires manual account selection."))
                puts(yellow("Please run this command on the server (nginx will keep running):"))
                puts(yellow("  sudo certbot certonly --webroot --webroot-path=%s -d %s" % (env.web_directory, env.domain_name)))
                puts(yellow("Then select option 1: web.omisli.si@2020-06-21T20:45:41Z (72b6)"))
                abort("Certificate setup requires manual intervention")
        else:
            puts(yellow("Certificate setup failed. Error:"))
            puts(result_str)
            raise

    puts(green("SSL certificate obtained successfully! Nginx was never stopped."))


def renew_certbot():
    """Renew Let's Encrypt certificates"""
    sudo("certbot renew")
    puts(green("Certificates renewed!"))


def setup():
    """Initial setup: nginx config, SSL certificate, and HTTP Basic Auth"""
    puts(green("Running initial setup..."))

    # Deploy nginx configuration
    nginxconfig()

    # Set up SSL certificate
    if env.secure:
        puts(yellow("Setting up SSL certificate (this may take a moment)..."))
        setup_certbot()

    # Set up HTTP Basic Auth
    setup_htpasswd()

    # Reload nginx
    nginxreload()

    puts(green("Setup complete!"))


def deploy():
    """Deploy dashboard: generate locally, sync files, and reload nginx"""
    puts(green("Deploying dashboard..."))

    # Check if oa command is available
    with hide('running', 'stdout', 'stderr'):
        result = local("which oa", capture=True)
        if result.return_code != 0:
            puts(yellow("⚠️  'oa' command not found in PATH."))
            puts(yellow("   Please activate your virtual environment first:"))
            puts(yellow("   source venv/bin/activate"))
            puts(yellow("   Then run: fab web deploy"))
            abort("'oa' command not available. Activate virtual environment and try again.")

    # Generate dashboard locally
    puts(green("Generating dashboard locally..."))
    local_dashboard = os.path.join(ROOT_DIR, "dashboard")
    local("oa generate-dashboard --output-dir %s" % local_dashboard)

    # Sync dashboard files
    sync_dashboard()

    # Reload nginx
    nginxreload()

    puts(green("Deployment complete!"))

