import React from "react";
const EntryAIPanel = ({ entry, stopLoss, takeProfit, reason }) => (
  <div className="panel entry-ai-panel">
    <h3>?? Trade Signal</h3>
    <p><strong>Entry:</strong> {entry}</p>
    <p><strong>Stop Loss:</strong> {stopLoss}</p>
    <p><strong>Take Profit:</strong> {takeProfit}</p>
    <p><strong>Reason:</strong> {reason}</p>
  </div>
);
export default EntryAIPanel;
