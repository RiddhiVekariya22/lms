<div align="center" markdown="1">

<img src=".github/lms-logo.png" alt="Frappe Learning logo" width="80" height="80"/>
<h1>LMS</h1>


### Key Features

- **Structured Learning**: Design a course with a 3-level hierarchy — courses, chapters, and lessons.
- **Quizzes and Assignments**: Single-choice, multiple-choice, or open-ended questions; PDF/document assignment submissions.
- **Certifications**: Grant certificates on course or batch completion using the built-in or a custom template.

---

## Structure

Understanding the relationship between these three concepts makes the setup steps much easier to follow.

### Bench

A **bench** is a self-contained directory that holds everything Frappe needs to run: the framework, your apps, a Python virtual environment, config files, and the scripts that manage processes. You create one with `bench init`, and from that point on every `bench` command you run must be executed from inside that directory.

```
frappe-bench/          ← the bench root
├── apps/              ← all installed apps live here
│   ├── frappe/        ← the core framework (always present)
│   ├── lms/           ← the LMS app
│   └── payments/      ← the Payments app
├── sites/             ← one sub-folder per site
│   └── lms.localhost/
├── env/               ← Python virtualenv
└── Procfile           ← defines the processes bench start launches
```

### Apps

An **app** is a Python/Vue package that adds features to Frappe. Apps live in `apps/` and are fetched with `bench get-app`. Fetching an app only downloads it — it is not active anywhere yet.

### Sites

A **site** is an independent Frappe installation with its own database, file storage, and settings. A single bench can host multiple sites. You create one with `bench new-site`.

### Putting it together

Installing an app **onto a site** is the step that activates it:

```bash
bench --site <sitename> install-app <appname>
```

This runs the app's database migrations against that site's database and registers the app there. The same app can be installed on some sites and not others within the same bench — each site is fully isolated.

So the full flow is always:

1. `bench init` — create the bench
2. `bench new-site` — create a site (and its database)
3. `bench get-app` — download an app into the bench
4. `bench --site <name> install-app` — activate the app on the site
5. `bench start` — boot all processes (web server, workers, scheduler)

---

## Development Setup

### Prerequisites

| Tool | Minimum Version |
|------|----------------|
| Python | 3.10+ |
| Node.js | 18+ |
| MariaDB | 10.6+ |
| Redis | 6+ |
| wkhtmltopdf | 0.12.6 (with patched Qt) |
| yarn | 1.12+ |

---

### Windows (via WSL 2)

Frappe bench does not run natively on Windows. The recommended approach is to use **WSL 2** (Windows Subsystem for Linux) with Ubuntu.

#### 1. Enable WSL 2

Open **PowerShell as Administrator** and run:

```powershell
wsl --install
```

Restart your machine when prompted. This installs WSL 2 with Ubuntu by default.

If WSL is already installed but you need Ubuntu:

```powershell
wsl --install -d Ubuntu
```

Set WSL 2 as the default version:

```powershell
wsl --set-default-version 2
```

#### 2. Open Ubuntu and update packages

```bash
sudo apt update && sudo apt upgrade -y
```

#### 3. Install system dependencies

```bash
sudo apt install -y \
  python3-dev python3-pip python3-venv \
  mariadb-server mariadb-client \
  redis-server \
  nodejs npm \
  git curl \
  libffi-dev libssl-dev \
  wkhtmltopdf \
  xvfb libfontconfig
```

Install yarn globally:

```bash
sudo npm install -g yarn
```

#### 4. Secure MariaDB

```bash
sudo mysql_secure_installation
```

When prompted:
- Set a root password (remember it — you'll need it for bench).
- Answer **Y** to all remaining prompts.

Then configure MariaDB for Frappe by editing the config:

```bash
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```

Add or update the `[mysqld]` section:

```ini
[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
```

Restart MariaDB:

```bash
sudo service mariadb restart
```

#### 5. Install frappe-bench

```bash
pip3 install frappe-bench
```

If the `bench` command is not found after install, add the local bin to your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### 6. Initialise a bench

```bash
bench init --frappe-branch version-15 frappe-bench
cd frappe-bench
```

#### 7. Create a new site

```bash
bench new-site lms.localhost
```

You will be prompted for the MariaDB root password set in step 4, and to set an Administrator password for the site.

#### 8. Get and install the LMS app

```bash
bench get-app https://github.com/your-org/lms
bench --site lms.localhost install-app lms
```

> Replace `https://github.com/your-org/lms` with the actual repository URL if it differs.

#### 9. Get and install the Payments app

```bash
bench get-app payments
bench --site lms.localhost install-app payments
```

#### 10. Map the site to localhost and start the server

```bash
bench --site lms.localhost add-to-hosts
bench start
```

Open [http://lms.localhost:8000](http://lms.localhost:8000) in your browser.  
Default credentials: **Username:** `Administrator` | **Password:** *(the one you set in step 7)*

---

### Linux (Ubuntu / Debian)

#### 1. Install system dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
  python3-dev python3-pip python3-venv \
  mariadb-server mariadb-client \
  redis-server \
  nodejs npm \
  git curl \
  libffi-dev libssl-dev \
  wkhtmltopdf \
  xvfb libfontconfig
```

Install yarn:

```bash
sudo npm install -g yarn
```

#### 2. Secure and configure MariaDB

```bash
sudo mysql_secure_installation
```

Edit the MariaDB server config:

```bash
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```

Add under `[mysqld]`:

```ini
[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
```

```bash
sudo systemctl restart mariadb
```

#### 3. Install frappe-bench

```bash
pip3 install frappe-bench
```

Ensure `~/.local/bin` is on your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### 4. Initialise a bench

```bash
bench init --frappe-branch version-15 frappe-bench
cd frappe-bench
```

#### 5. Create a new site

```bash
bench new-site lms.localhost
```

Enter your MariaDB root password when prompted, then set an Administrator password for the site.

#### 6. Get and install the LMS app

```bash
bench get-app https://github.com/your-org/lms
bench --site lms.localhost install-app lms
```

#### 7. Get and install the Payments app

```bash
bench get-app payments
bench --site lms.localhost install-app payments
```

#### 8. Start the development server

```bash
bench --site lms.localhost add-to-hosts
bench start
```

Open [http://lms.localhost:8000](http://lms.localhost:8000) in your browser.

---

## Troubleshooting

**`bench` command not found**  
Add `~/.local/bin` to PATH (see the PATH export step above).

**MariaDB access denied**  
Make sure you ran `mysql_secure_installation` and are supplying the correct root password.

**Node/yarn version mismatch**  
Use [nvm](https://github.com/nvm-sh/nvm) to manage Node versions: `nvm install 18 && nvm use 18`.

**wkhtmltopdf PDF errors on WSL**  
Install the version with patched Qt from the [wkhtmltopdf releases page](https://github.com/wkhtmltopdf/packaging/releases).

---

## Under the Hood

- [**Frappe Framework**](https://github.com/frappe/frappe): A full-stack web application framework.
- [**Frappe UI**](https://github.com/frappe/frappe-ui): A Vue-based UI library for modern interfaces.
- [**Payments App**](https://github.com/frappe/payments): Handles payment gateway integrations for course enrollments.

---

<br>
<div align="center" style="padding-top: 0.75rem;">
	<a href="https://frappe.io" target="_blank">
		<picture>
			<source media="(prefers-color-scheme: dark)" srcset="https://frappe.io/files/Frappe-white.png">
			<img src="https://frappe.io/files/Frappe-black.png" alt="Frappe Technologies" height="28"/>
		</picture>
	</a>
</div>
