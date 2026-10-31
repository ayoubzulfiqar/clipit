## Description

Please provide a clear and concise summary of the changes made in this pull request and the rationale behind them.

Closes # (issue reference if applicable)

---

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] ♻️ Code refactoring / performance optimization
- [ ] 📝 Documentation update
- [ ] 🧪 Testing and CI improvement
- [ ] 🎨 Subtitle styling / frontend UI polish

---

## How Has This Been Tested?

Please describe the tests you ran to verify your changes. Include steps so reviewers can reproduce.

- **Automated Tests**:
  ```bash
  python3 -m unittest discover -s tests
  # or
  pytest tests/ -v
  ```
- **Frontend Verification** (if modifying `web/dashboard`):
  ```bash
  npm run build --prefix web/dashboard
  ```
- **Manual Verification**: (CLI command or Web Studio job tested)

---

## Visual Verification (if applicable)

If this PR alters UI components, subtitle layouts, split-screen video crops, or theme styling, please attach before/after screenshots or clip previews here.

---

## Checklist

- [ ] My code adheres to the project's coding conventions and formatting standards.
- [ ] I have performed a self-review of my own code.
- [ ] I have commented my code, particularly in complex mathematical or video filter sections.
- [ ] I have added comprehensive unit tests that prove my fix or feature works as intended.
- [ ] New and existing unit tests pass locally with my changes.
- [ ] My commits follow [Conventional Commits](https://www.conventionalcommits.org/) format.
- [ ] I have updated corresponding documentation (`README.md`, `Usage.md`, etc.) where necessary.
- [ ] I have checked that no sensitive API keys, secrets, or temporary files are committed.
