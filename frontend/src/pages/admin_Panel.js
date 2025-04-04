import React, { useState, useEffect } from "react";
import { Bar, Line } from "react-chartjs-2";
import "chart.js/auto";
import "./AdminPanel.css"; // Importamos el archivo CSS

const AdminPanel = () => {
  const [selectedMonth, setSelectedMonth] = useState("2025-03");
  const [userInfo, setUserInfo] = useState(null);
  const [energyData, setEnergyData] = useState(null);
  const [changeRateData, setChangeRateData] = useState(null);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/users`)
      .then((res) => res.json())
      .then((data) => setUserInfo(data));

    fetch(`http://127.0.0.1:8000/consumo_energetico?mes=${selectedMonth}`)
      .then((res) => res.json())
      .then((data) => setEnergyData(data));

    fetch(`http://127.0.0.1:8000/tasa_cambio/1?mes=${selectedMonth}`)
      .then((res) => res.json())
      .then((data) => setChangeRateData(data));
  }, [selectedMonth]);

  const months = ["2025-01", "2025-02", "2025-03", "2025-04"];

  return (
    <div className="admin-panel">
      {/* Información del usuario */}
      <div className="user-info">
        <h2>Información del Usuario</h2>
        {userInfo && (
          <div>
            <p><strong>Nombre:</strong> {userInfo.Nombre}</p>
            <p><strong>Edad:</strong> {userInfo.edad}</p>
            <p><strong>Peso:</strong> {userInfo.Peso} kg</p>
          </div>
        )}
      </div>

      {/* Botones de selección de mes */}
      <div className="month-buttons">
        {months.map((month) => (
          <button
            key={month}
            onClick={() => setSelectedMonth(month)}
            className={`month-button ${selectedMonth === month ? "active" : ""}`}
          >
            {month}
          </button>
        ))}
      </div>

      {/* Gráficas */}
      <Charts energyData={energyData} changeRateData={changeRateData} />
    </div>
  );
};

// Componente Charts
const Charts = ({ energyData = {}, changeRateData = {} }) => {
  return (
    <div className="charts">
      {/* Gráfica de Consumo Energético */}
      <div className="chart-container">
        <h2>Consumo Energético</h2>
        {energyData && (
          <Bar
            data={{
              labels: ["Proteína", "Carbohidrato", "Grasa"],
              datasets: [
                {
                  label: "Consumo Energético",
                  data: [
                    energyData.Proteina || 0,
                    energyData.Carbohidrato || 0,
                    energyData.Grasa || 0,
                  ],
                  backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
                },
              ],
            }}
            options={{ responsive: true }}
          />
        )}
      </div>

      {/* Gráfica de Tasa de Cambio */}
      <div className="chart-container">
        <h2>Tasa de Cambio</h2>
        {changeRateData && (
          <Line
            data={{
              labels: ["Mes Anterior", "Mes Actual"],
              datasets: [
                {
                  label: "Tasa de Cambio (%)",
                  data: [
                    changeRateData.consumo_anterior || 0,
                    changeRateData.consumo_actual || 0,
                  ],
                  borderColor: "#4BC0C0",
                  fill: false,
                },
              ],
            }}
            options={{ responsive: true }}
          />
        )}
      </div>
    </div>
  );
};

export default AdminPanel;

