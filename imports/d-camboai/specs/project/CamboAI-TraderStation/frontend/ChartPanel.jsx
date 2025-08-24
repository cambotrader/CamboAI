import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import "chart.js/auto";
export default function ChartPanel() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetch("http://127.0.0.1:8000/chart")
      .then((res) => res.json())
      .then((json) => setData(json.chart));
  }, []);
  if (!data) return <div>Loading chart...</div>;
  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: "Price Movement",
        data: data.values,
        fill: false,
        borderColor: "#00BFFF",
        tension: 0.1,
      },
    ],
  };
  return (
    <div style={{ width: "600px", margin: "2rem auto" }}>
      <Line data={chartData} />
    </div>
  );
}
