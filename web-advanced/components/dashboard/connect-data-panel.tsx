"use client";
import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function ConnectDataPanel() {
  const [open, setOpen] = useState(false);
  const [apiBase, setApiBase] = useState<string>("");
  const [apiKey, setApiKey] = useState<string>("");
  const [binanceKey, setBinanceKey] = useState<string>("");
  const [binanceSecret, setBinanceSecret] = useState<string>("");
  const [alpacaKey, setAlpacaKey] = useState<string>("");
  const [alpacaSecret, setAlpacaSecret] = useState<string>("");

  return (
    <div className="mb-4">
      <Button variant="outline" size="sm" onClick={() => setOpen(!open)}>
        {open ? "Close" : "Connect Data"}
      </Button>
      {open && (
        <Card className="mt-3">
          <CardHeader>
            <CardTitle>Connect Data Sources</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="text-sm font-medium">Backend API</div>
                <input
                  className="w-full p-2 border rounded"
                  placeholder="https://api.your-backend.com"
                  value={apiBase}
                  onChange={(e) => setApiBase(e.target.value)}
                />
                <input
                  className="w-full p-2 border rounded"
                  placeholder="X-API-Key"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                />
                <div className="text-xs text-gray-500">Used for calling your protected backend endpoints.</div>
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium">Binance (public/spot)</div>
                <input
                  className="w-full p-2 border rounded"
                  placeholder="API Key"
                  value={binanceKey}
                  onChange={(e) => setBinanceKey(e.target.value)}
                />
                <input
                  className="w-full p-2 border rounded"
                  placeholder="API Secret"
                  value={binanceSecret}
                  onChange={(e) => setBinanceSecret(e.target.value)}
                />
                <div className="text-xs text-gray-500">Optional. Public endpoints work without keys.</div>
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium">Alpaca (paper trading)</div>
                <input
                  className="w-full p-2 border rounded"
                  placeholder="API Key"
                  value={alpacaKey}
                  onChange={(e) => setAlpacaKey(e.target.value)}
                />
                <input
                  className="w-full p-2 border rounded"
                  placeholder="API Secret"
                  value={alpacaSecret}
                  onChange={(e) => setAlpacaSecret(e.target.value)}
                />
                <div className="text-xs text-gray-500">For paper trading later. Not required for demo.</div>
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium">Website Login (embed)</div>
                <input className="w-full p-2 border rounded" placeholder="Email (for future OAuth)" />
                <input className="w-full p-2 border rounded" placeholder="Password" type="password" />
                <div className="text-xs text-gray-500">Placeholder. We will swap to Email/OAuth flows.</div>
              </div>
            </div>

            <div className="mt-4 flex gap-2">
              <Button size="sm" onClick={() => alert("Saved locally for this session (demo)")}>Save</Button>
              <Button size="sm" variant="outline" onClick={() => {
                setApiBase(""); setApiKey(""); setBinanceKey(""); setBinanceSecret(""); setAlpacaKey(""); setAlpacaSecret("");
              }}>Reset</Button>
            </div>

            <div className="text-xs text-gray-500 mt-3">
              For production, we will store secrets securely (server-side or vault). This demo never persists keys.
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}