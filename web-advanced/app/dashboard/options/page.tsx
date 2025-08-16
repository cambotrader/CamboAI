"use client";
import React, { useEffect, useState } from 'react';
import { getPresets, priceMultiLeg } from '@/lib/api/client';

export default function OptionsDemoPage() {
  const [presets, setPresets] = useState<any>({});
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    getPresets().then(setPresets).catch(console.error);
  }, []);

  async function runSample() {
    const payload = {
      preset: 'balanced',
      legs: [
        { right: 'call', side: 'long', qty: 1, strike: 100, expiry: 0.5, vol: 0.2, rate: 0.01, div_yield: 0, spot: 105 },
        { right: 'call', side: 'short', qty: 1, strike: 110, expiry: 0.5, vol: 0.2, rate: 0.01, div_yield: 0, spot: 105 },
      ],
    };
    const r = await priceMultiLeg(payload);
    setResult(r);
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Options Pricing (Demo)</h1>
      <div>
        <button className="px-3 py-2 bg-blue-600 text-white rounded" onClick={runSample}>Price Sample Spread</button>
      </div>
      <pre className="bg-gray-900 text-gray-100 p-4 rounded text-sm overflow-auto">
        {JSON.stringify({ presets, result }, null, 2)}
      </pre>
    </div>
  );
}