import React from "react";
const NetPanel = ({ netPosition, pnl }) => (
  <div className="panel net-panel">
    <h3>?? Net Summary</h3>
    <p><strong>Net Position:</strong> {netPosition}</p>
    <p><strong>PnL:</strong> {pnl}</p>
  </div>
);
export default NetPanel;
