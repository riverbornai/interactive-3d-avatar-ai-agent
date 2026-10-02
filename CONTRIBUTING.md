# Contributing to Interactive 3D Avatar AI Agent

Thank you for your interest in improving this project, built by
[Riverborn Limited](https://riverborn.com). Bug reports, ideas and pull
requests are welcome.

Please read this document before opening an issue or a pull request.

---

## License of contributions

This project is licensed under the [MIT License](LICENSE). By submitting a
contribution (code, documentation or assets), you agree that it is licensed
under the same MIT License. Only submit work you have the right to contribute.

---

## Code of Conduct

Please keep discussions respectful, welcoming and professional.

---

## Reporting Bugs

Before opening an issue, check the existing issues to see whether it has
already been reported.

When opening a bug report, please include:
- A clear, descriptive title.
- Steps to reproduce the issue.
- Expected behavior vs. actual behavior.
- Error logs from your terminal (backend) or browser console (frontend).
  Remove any API keys from logs before posting.
- Your system configuration (OS, Python version, browser name and version).

---

## Suggesting Enhancements

- Open a **Feature Request** issue.
- Describe the feature and *why* it would be useful.
- If possible, include mockups or code snippets showing how it might work.

---

## Local Development Setup

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/interactive-3d-avatar-ai-agent.git
   cd interactive-3d-avatar-ai-agent
   ```
3. **Set up the upstream remote** to keep your fork in sync:
   ```bash
   git remote add upstream https://github.com/riverbornai/interactive-3d-avatar-ai-agent.git
   ```
4. **Create a virtual environment** and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
5. **Configure your environment**:
   Copy `.env.example` to `.env` and fill in your keys. Never commit `.env`.
   The repository already includes an avatar at `static/avatar_fixed.glb`; if
   you swap it, use a `.glb` with ARKit blendshapes.
6. **Run the server** from the repository root with `python server.py` and
   open <http://localhost:8000>.

---

## Code Style Guidelines

### Python (Backend)
- Follow **PEP 8**.
- Use descriptive variable and function names.
- Keep functions small and single-purpose.
- Write docstrings for public functions and endpoints.

### JavaScript & HTML (Frontend)
- Use modern **ES6+** syntax.
- Keep DOM interactions simple.
- If you change the blendshape mapping, make sure it still matches the 55
  ARKit names in `static/blendshapes.js` and their order in Azure TTS output.
- Keep the UI responsive and consistent with the existing styles.

---

## Submitting a Pull Request

1. **Create a new branch** for your work:
   ```bash
   git checkout -b feature/your-feature
   # or
   git checkout -b bugfix/describe-the-bug
   ```
2. **Write your code** and test it locally.
3. **Commit your changes** with a clear message:
   ```bash
   git commit -m "feat: add volume threshold setting to the UI"
   ```
4. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature
   ```
5. **Open a Pull Request** against the `main` branch of the upstream repository.
6. Explain your changes in the PR description and reference related issues
   (e.g., `Closes #12`).

---

## Need Help?

If you have questions about the codebase or the contribution process, open an
issue, or email [hello@riverborn.com](mailto:hello@riverborn.com).
