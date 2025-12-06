## Licensing

**Software**: Cryptonote is free and open-source software. You can use, modify, and distribute it freely.

**AI Prompts**: Access to our premium, curated AI prompt libraries requires a paid license. The free version includes only basic sample prompts to demonstrate functionality.

For licensing inquiries, please contact us at [your contact information].

A secure, offline, standalone note-taking application designed for high-security environments.

**Free Software, Premium AI Prompts**: The Cryptonote application is completely free to use. However, access to curated AI prompt libraries requires a premium license.

## Features

-   **Military-Grade Encryption:** Uses AES-256-GCM for encryption and Argon2id for key derivation.
-   **Offline & Standalone:** No internet connection required. No auto-updates.
-   **Single File Database:** All data is stored in a single encrypted file (`notes.enc`), making backups easy.
-   **Secure Import/Export:** Import and export libraries with encryption.
-   **Developer Friendly:** "Copy Content Only" feature to quickly copy code snippets or prompts without titles.
-   **File Attachments:** Attach files to notes for reference.
-   **Screen Snipping:** "📷 Snip" button launches Windows Snip & Sketch tool for capturing screenshots, which can be added to new or existing notes.
-   **Clipboard History:** "📋 Clipboard" button opens a floating panel showing history of copied items (text and images), allowing quick access and pasting. Can be disabled in settings.
-   **Settings:** "⚙️ Settings" button opens configuration dialog to toggle features like clipboard history.
-   **Lifetime License:** Purchase a one-time lifetime license via PayPal to unlock Ollama AI features for unlimited local AI assistance.
-   **Token System:** Purchase AI tokens via PayPal for OpenAI usage. Tokens are deducted per AI fix request.
-   **Token Tracking:** Displays current token balance and lifetime total tokens used in the header.
-   **Sample Prompts Download:** Download free sample AI prompts (limited in freeware).
-   **Post-It Board UI:** Visual card-based interface for easy note management.
-   **Dark Theme GUI:** Modern, secure, and visually appealing interface using CustomTkinter.

## Security Details

-   **Cipher:** AES-256-GCM (Authenticated Encryption)
-   **Key Derivation Function (KDF):** Argon2id
    -   Memory Cost: 64 MB
    -   Time Cost: 2 iterations
    -   Parallelism: 2 threads
-   **Salt:** 16 bytes (randomly generated per file)
-   **Nonce:** 12 bytes (randomly generated per encryption)

## How to Run (Source)

1.  Install Python 3.10+.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up AI assistance:
    - For Ollama (lifetime license required): Install Ollama from https://ollama.ai/, pull a model (e.g., `ollama pull llama2`), and activate lifetime license in app.
    - For OpenAI: Set API key and buy tokens:
      ```bash
      export OPENAI_API_KEY="your-openai-api-key"
      ```
4.  Set PayPal credentials for license verification:
    ```bash
    export PAYPAL_EMAIL="yourpaypal@email.com"
    export PAYPAL_CLIENT_ID="your-paypal-client-id"
    export PAYPAL_CLIENT_SECRET="your-paypal-client-secret"
    ```
4.  Set up Google Drive (optional, for cloud backup):
    - Go to [Google Cloud Console](https://console.cloud.google.com/)
    - Create a new project or select existing
    - Enable Google Drive API
    - Create OAuth 2.0 credentials (Desktop application)
    - Download the `client_secret.json` file and place it in the app directory
5.  Run the application:
    ```bash
    python Gui.py
    ```

## How to Build (Standalone .exe)

1.  Run the build script:
    ```cmd
    build_exe.bat
    ```
2.  The standalone executable will be created in the `dist` folder as `Cryptonote.exe`.
3.  You can move this `.exe` file anywhere. It requires no installation.

## Usage

1.  **Create/Open Database:** Launch the app. Select a file (or create a new one) and enter your master password.
2.  **Snip Screen:** Click the "📷 Snip" button to capture screenshots and add them to notes.
3.  **Clipboard History:** Click "📋 Clipboard" to view and paste from clipboard history (can be disabled in settings).
4.  **Settings:** Click "⚙️ Settings" to configure app features.
4.  **Add Note:** Click "New Note", enter title, content, and tags. Click "Save".
4.  **Edit Note:** Click on a note card to open the edit popup.
5.  **Attach Files:** In the edit popup, use "Attach/Replace" to add files to notes.
6.  **Copy Content:** Click the orange "Copy Content Only" button to copy the body of the note to the clipboard without the title.
7.  **Fix with AI:** Click "Fix with AI" to use Ollama (if lifetime license activated) or OpenAI (if tokens available) to improve the content.
8.  **Extras:** Click "Extras" to open the shop for purchasing tokens or lifetime license.
7.  Download Prompts:** Click "Download Prompts" to add free sample prompts to your library.
8.  Upload to Google Drive:** Click "Upload to Drive" to backup your encrypted database to Google Drive (requires setup).
9.  Import/Export:** Use the buttons in the header to securely import or export your library.
10. Backup:** Simply copy the `notes.enc` file (or whatever you named it) to a secure location.
