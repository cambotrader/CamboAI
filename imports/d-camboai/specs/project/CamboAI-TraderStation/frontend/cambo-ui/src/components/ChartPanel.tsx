import React from "react";
import Plot from "react-plotly.js";
const ChartPanel = ({ data, layout }) => (
  <div className="panel chart-panel">
    <Plot data={data} layout={layout} />
  </div>
);
export default ChartPanel;
