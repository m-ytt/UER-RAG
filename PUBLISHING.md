# Publishing the verified release

The canonical public repository is <https://github.com/m-ytt/UER-RAG>. Version
`1.2.0` aligns the public artifacts with the fact-checked manuscript, removes
unsupported cross-model aggregates, and replaces them with the reproducible
PopQA split-sensitivity analysis.

## Preferred: Git command line

```bash
git clone https://github.com/m-ytt/UER-RAG.git
cd UER-RAG
# Copy the verified package contents into this directory.
git add -A
git commit -m "Release verified UER-RAG v1.2.0"
git push origin main
git tag -a v1.2.0 -m "UER-RAG v1.2.0"
git push origin v1.2.0
```

## GitHub web upload

1. Open the repository's **Code** page and remain at the root of `main`.
2. Choose **Add file → Upload files**.
3. Extract the release ZIP locally. Drag the *contents* of the extracted folder,
   not the outer folder itself, into the upload area.
4. Confirm that `README.md`, `src`, `tests`, `analysis`, and `configs` appear at
   the repository root. Do not create a second nested `UER-RAG/` directory.
5. Commit with the message `Release verified UER-RAG v1.2.0`.
6. Because some browsers omit hidden paths during drag-and-drop, verify that
   `.gitignore`, `.env.example`, and `.github/workflows/tests.yml` are present.
   Add any missing hidden file manually with **Add file → Create new file**.
7. Open **Actions** and confirm that the test matrix passes.
8. Create a release/tag named `v1.2.0` from the repository's Releases page.

Before committing, confirm that no `.env`, API key, raw provider response,
retrieved Wikipedia passage dump, or private corpus file appears in the staged
file list.
