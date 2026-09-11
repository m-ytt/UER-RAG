# Publishing to GitHub

The repository is already initialized on branch `main` and contains one clean
release commit. Before public release:

1. Create an empty public GitHub repository named `UER-RAG` (do not add a
   README or license on GitHub).
2. Replace `OWNER` in `CITATION.cff` with the GitHub account or organization.
3. Replace `<GITHUB_URL>` in both manuscript files with the final public URL.
4. Add and push the remote:

```bash
git remote add origin https://github.com/OWNER/UER-RAG.git
git push -u origin main
```

Do not commit `.env`, API credentials, retrieved Wikipedia passages, or raw
model outputs containing corpus text.
