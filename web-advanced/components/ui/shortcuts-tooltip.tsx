"use client";
import React, { useState } from "react";

export function ShortcutsTooltip() {
  const [open, setOpen] = useState(false);
  return (
    <div className="relative inline-block">
      <button className="text-xs text-gray-500 underline" onClick={() => setOpen(o => !o)}>Shortcuts</button>
      {open && (
        <div className="absolute z-50 mt-2 w-64 rounded-md border bg-white p-3 text-xs shadow">
          <div className="font-semibold mb-1">Keyboard Shortcuts</div>
          <ul className="space-y-1">
            <li><code>R</code> — Reload data</li>
            <li><code>←</code> — Shift window backward (Last)</li>
            <li><code>→</code> — Shift window forward (Next)</li>
          </ul>
        </div>
      )}
    </div>
  );
}