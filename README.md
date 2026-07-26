Minecraft Server Installer.

A simple and lightweight Bash-based installer for creating Minecraft servers from your terminal.

Instead of manually downloading server files, accepting the EULA, creating startup scripts, and configuring folders, this tool automates the entire process with an easy interactive menu.

«⚠️ Note: The installer is currently available only in Spanish. An English translation is planned for a future release.»

---

✨ Features

- Interactive terminal interface
- Automatic server download
- Automatic EULA acceptance
- Startup script generation
- RAM selection during installation
- Creates a clean server directory structure
- Designed to be lightweight and dependency-free (except for common Linux tools)

---

📦 Supported Server Software

Currently supported:

- ✅ Vanilla
- ✅ Paper
- ✅ Purpur
- ✅ Fabric
- ✅ Forge (modern versions)
- ✅ NeoForge

More server software may be added in future releases.

---

📋 Requirements

Before using the installer, make sure you have:

- Linux
- Bash
- Java
- "curl"
- "jq"

Example (Debian/Ubuntu):

sudo apt update
sudo apt install openjdk-21-jre curl jq

---

🚀 Installation & Usage

### Running with Python 3 (Recommended)
```bash
python3 installer.py
```

### Running with Bash
```bash
chmod +x installer.sh
./installer.sh
```

---

🖥️ How It Works

The installer will guide you through a few simple steps:

1. Select the server software.
2. Choose a supported Minecraft version.
3. Enter a server name.
4. Select the amount of RAM.
5. Wait while the installer downloads and prepares everything automatically.

Once finished, your server directory will contain everything required to start the server immediately.

For Forge and NeoForge, the installer also performs the server installation process automatically.

---

📁 Generated Structure

A typical server directory looks like this:

MyServer/
├── eula.txt
├── logs/
├── start.sh
├── server.jar
└── ...

Forge and NeoForge installations will generate their own files according to their official installers.

---

🎯 Project Goals

This project aims to provide a fast and easy way to create Minecraft servers without requiring users to manually search for downloads, install loaders, or configure startup scripts.

The focus is on:

- Simplicity
- Automation
- Compatibility
- Clean code
- Easy maintenance

---

🤝 Contributions

Contributions, suggestions, and bug reports are always welcome.

Feel free to open an Issue or submit a Pull Request.

---

📄 License

This project is released under the MIT License.
