"use client";
import React, { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";

export type DateRange = { from?: string; to?: string };

const presets = [
  { key: "1d", label: "1D" },
  { key: "5d", label: "5D" },
  { key: "1mo", label: "1M" },
  { key: "3mo", label: "3M" },
  { key: "6mo", label: "6M" },
  { key: "1y", label: "1Y" },
  { key: "ytd", label: "YTD" },
  { key: "max", label: "Max" },
  { key: "custom", label: "Custom" },
] as const;

export function DateRangeCompact({ value, onChange }: { value: DateRange; onChange: (v: DateRange, preset?: string) => void }) {
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<string>("1mo");
  const [from, setFrom] = useState<string>(value.from || "");
  const [to, setTo] = useState<string>(value.to || "");

  const label = useMemo(() => {
    const p = presets.find(p => p.key === mode);
    if (mode === "custom") return from && to ? `${from} → ${to}` : "Custom";
    return p?.label || "Range";
  }, [mode, from, to]);

  function apply(preset: string) {
    setMode(preset);
    if (preset !== "custom") {
      onChange({ from: "", to: "" }, preset);
      setOpen(false);
    }
  }

  function applyCustom() {
    if (from && to) {
      onChange({ from, to }, "custom");
      setOpen(false);
    }
  }

  return (
    <div className="relative inline-block">
      <Button size="sm" variant="outline" onClick={() => setOpen(o => !o)}>{label}</Button>
      {open && (
        <div className="absolute z-50 mt-2 w-72 rounded-md border bg-white p-3 shadow">
          <div className="grid grid-cols-5 gap-2 mb-3">
            {presets.map(p => (
              <button
                key={p.key}
                onClick={() => apply(p.key)}
                className={`text-xs px-2 py-1 rounded border ${mode === p.key ? 'bg-blue-600 text-white border-blue-600' : 'hover:bg-gray-50'}`}
              >{p.label}</button>
            ))}
          </div>
          {mode === 'custom' && (
            <div className="grid grid-cols-2 gap-2">
              <input type="date" className="p-2 border rounded" value={from} onChange={e => setFrom(e.target.value)} />
              <input type="date" className="p-2 border rounded" value={to} onChange={e => setTo(e.target.value)} />
              <div className="col-span-2 flex justify-end gap-2">
                <Button size="sm" variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                <Button size="sm" onClick={applyCustom}>Apply</Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}