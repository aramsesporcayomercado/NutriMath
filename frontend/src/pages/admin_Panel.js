import React, { useState, useEffect } from "react";
import { Bar, Line } from "react-chartjs-2";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import "chart.js/auto";

const AdminPanel = () => {
    const [selectedMonth, setSelectedMonth] = useState("2025-03");
    const [userInfo, setUserInfo] = useState(null);
    const [energyData, setEnergyData] = useState(null);
    const [changeRateData, setChangeRateData] = useState(null);

    useEffect(() => {
        fetch(`https://127.0.0.1:8000/users`)
            .then((res) => res.json())
            .then((data) => setUserInfo(data));

        fetch(`https://127.0.0.1:8000/consumo_energetico?mes=${selectedMonth}`)
            .then((res) => res.json())
            .then((data) => setEnergyData(data));

        fetch(`https://127.0.0.1:8000/tasa_cambio/1?mes=${selectedMonth}`)
            .then((res) => res.json())
            .then((data) => setChangeRateData(data));
    }, [selectedMonth]);

    const months = ["2025-01", "2025-02", "2025-03", "2025-04"];

    return (
        <div className="p-6 grid grid-cols-4 gap-4">
            {/* Información del usuario */}
            <Card className="col-span-4 md:col-span-1 p-4 bg-white shadow-lg rounded-2xl">
                <h2 className="text-xl font-bold">Información del Usuario</h2>
                {userInfo && (
                    <div className="mt-2">
                        <p><strong>Nombre:</strong> {userInfo.nombre}</p>
                        <p><strong>Edad:</strong> {userInfo.edad}</p>
                        <p><strong>Peso:</strong> {userInfo.peso} kg</p>
                    </div>
                )}
            </Card>

            {/* Botones de selección de mes */}
            <div className="col-span-4 flex justify-center gap-2">
                {months.map((month) => (
                    <Button key={month} onClick={() => setSelectedMonth(month)}>
                        {month}
                    </Button>
                ))}
            </div>

            {/* Gráficas */}
            <Card className="col-span-4 md:col-span-2 p-4 bg-white shadow-lg rounded-2xl">
                <h2 className="text-lg font-bold">Consumo Energético</h2>
                {energyData && (
                    <Bar
                        data={{
                            labels: ["Proteína", "Carbohidrato", "Grasa"],
                            datasets: [
                                {
                                    label: "Consumo Energético",
                                    data: [energyData.Proteina, energyData.Carbohidrato, energyData.Grasa],
                                    backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
                                },
                            ],
                        }}
                    />
                )}
            </Card>

            <Card className="col-span-4 md:col-span-2 p-4 bg-white shadow-lg rounded-2xl">
                <h2 className="text-lg font-bold">Tasa de Cambio</h2>
                {changeRateData && (
                    <Line
                        data={{
                            labels: ["Mes Anterior", "Mes Actual"],
                            datasets: [
                                {
                                    label: "Tasa de Cambio (%)",
                                    data: [changeRateData.consumo_anterior, changeRateData.consumo_actual],
                                    borderColor: "#4BC0C0",
                                    fill: false,
                                },
                            ],
                        }}
                    />
                )}
            </Card>
        </div>
    );
};

export default AdminPanel;
