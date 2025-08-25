# Archived Snapshots

This directory will store unique historical variants of modules (chart_module, strategy_engine, sentiment_panel, etc.) after consolidation.

Process (planned):
1. Hash all candidate duplicate filenames.
2. Keep canonical version in /modules or /modules/strategy /modules/panels.
3. Copy differing legacy variants here with suffix __variantX.
4. Emit consolidation_manifest.json documenting mapping.

Created 2025-08-24.
