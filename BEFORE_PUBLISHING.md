# Before Publishing to GitHub

## 1. Update Repository URLs

In `README.md`:
- Line ~271: Replace `[yourusername]` with your GitHub username

In `LICENSE.txt`:
- Line ~43: Add your GitHub repository URL:
  ```
  url = {https://github.com/yourusername/HapticCollectionMediaPlayer}
  ```

## 2. Clean Up Files

Remove test/debug files (optional):
```bash
rm test_nfc.py debug_nfc.py simple_nfc_server.py diagnose_nfc.py
rm run_from_python_dir.sh
rm nfc_player.py start_nfc_system.py start_nfc_system.sh run_nfc_system.sh
rm README_*.md  # Remove old READMEs
```

## 3. Check .gitignore

Make sure these are in your .gitignore:
- `nfc_mappings.json` (personal mappings)
- `nfc_player.log`
- Any personal HTML content you don't want to share

## 4. Create Initial Release

Consider tagging your first release:
```bash
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0
```

## 5. Add Description on GitHub

When creating the repository, add:
- **Description**: "Interactive NFC-based media display system for exhibitions and installations"
- **Topics**: `nfc`, `raspberry-pi`, `exhibition`, `interactive`, `museum`, `python`, `flask`
- **Homepage**: You could add a demo video link later

## 6. Consider Adding

- `CONTRIBUTING.md` - If you want contributions
- Example content in `html_content/` - So people can test immediately
- Photos/videos in README - Shows the system in action

Good luck with your publication! 🚀
