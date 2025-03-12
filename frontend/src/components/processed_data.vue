<template>
  <div class="chart-container">
    <!-- SCG Logo -->
    <div class="scg-logo">
      <img src="@/assets/SCGP_Logo_Full-Version.webp" alt="SCG Logo" />
    </div>

    <!-- Chart Canvas -->
    <canvas ref="chartCanvas"></canvas>
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import Chart from "chart.js/auto";
import axios from "axios";

export default {
  name: "SensorChart",
  setup() {
    const chartCanvas = ref(null);
    const chartData = ref({
      timestamps: [],
      temperature: [],
      humidity: [],
      air_quality: [],
      anomalies: {
        temperature: [],
        humidity: [],
        air_quality: [],
      },
    });
    const isLoading = ref(true);
    const errorMessage = ref("");

    const fetchData = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/sensor/processed/");
        const data = response.data;

        // Ensure data exists
        if (data && data.timestamps && data.data) {
          chartData.value = {
            timestamps: data.timestamps,
            temperature: data.data.temperature,
            humidity: data.data.humidity,
            air_quality: data.data.air_quality,
            anomalies: data.anomalies,
          };
          renderChart();
        } else {
          errorMessage.value = "Data structure is incorrect.";
        }
      } catch (error) {
        errorMessage.value = "Failed to fetch data.";
        console.error("Error fetching data:", error);
      } finally {
        isLoading.value = false;
      }
    };

    const renderChart = () => {
      const ctx = chartCanvas.value.getContext("2d");

      // Anomalies detection: highlight anomalies in the data
      const temperatureAnomalies = chartData.value.anomalies.temperature.map(
        (value, index) => (value !== null ? chartData.value.timestamps[index] : null)
      );
      const humidityAnomalies = chartData.value.anomalies.humidity.map(
        (value, index) => (value !== null ? chartData.value.timestamps[index] : null)
      );
      const airQualityAnomalies = chartData.value.anomalies.air_quality.map(
        (value, index) => (value !== null ? chartData.value.timestamps[index] : null)
      );

      new Chart(ctx, {
        type: "line", // Line chart
        data: {
          labels: chartData.value.timestamps, // X-axis (timestamps)
          datasets: [
            {
              label: "Temperature",
              data: chartData.value.temperature,
              borderColor: "#FF4C00", // SCG red
              fill: false,
              pointBackgroundColor: chartData.value.anomalies.temperature.map(
                (value) => (value !== null ? "red" : "transparent")
              ),
              pointRadius: 5,
              pointHoverRadius: 8,
            },
            {
              label: "Humidity",
              data: chartData.value.humidity,
              borderColor: "#0066B2", // SCG blue
              fill: false,
              pointBackgroundColor: chartData.value.anomalies.humidity.map(
                (value) => (value !== null ? "blue" : "transparent")
              ),
              pointRadius: 5,
              pointHoverRadius: 8,
            },
            {
              label: "Air Quality",
              data: chartData.value.air_quality,
              borderColor: "#00B5E2", // SCG turquoise
              fill: false,
              pointBackgroundColor: chartData.value.anomalies.air_quality.map(
                (value) => (value !== null ? "green" : "transparent")
              ),
              pointRadius: 5,
              pointHoverRadius: 8,
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            x: {
              type: "category", // Use 'category' type for the x-axis
              title: {
                display: true,
                text: "Timestamp",
              },
            },
            y: {
              type: "linear", // Linear scale for the y-axis
              title: {
                display: true,
                text: "Sensor Value",
              },
            },
          },
          elements: {
            point: {
              radius: 5, // Adjust point size
              hoverRadius: 8,
            },
          },
          tooltips: {
            enabled: true,
            callbacks: {
              label: function (tooltipItem) {
                const datasetIndex = tooltipItem.datasetIndex;
                const dataIndex = tooltipItem.index;
                let value = tooltipItem.raw;
                let label = tooltipItem.label;

                // Check if the value is an anomaly
                if (
                  (datasetIndex === 0 && chartData.value.anomalies.temperature[dataIndex] !== null) ||
                  (datasetIndex === 1 && chartData.value.anomalies.humidity[dataIndex] !== null) ||
                  (datasetIndex === 2 && chartData.value.anomalies.air_quality[dataIndex] !== null)
                ) {
                  value = `${value} (Anomaly)`;
                  label = `Anomaly detected at ${label}`;
                }

                return `${label}: ${value}`;
              },
            },
          },
        },
      });
    };

    onMounted(() => {
      fetchData();
    });

    return {
      chartCanvas,
      isLoading,
      errorMessage,
    };
  },
};
</script>

<style scoped>
/* Style the container to match SCG branding */
.chart-container {
  background-color: #f2f2f2; /* Light grey background to match SCG's branding */
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.scg-logo img {
  max-width: 200px; /* Adjust logo size */
  margin-bottom: 20px;
}

canvas {
  max-width: 100%;
  height: 400px;
  margin-top: 20px;
  background-color: #333; /* Dark background for the chart */
  border-radius: 8px;
}

.error-message {
  color: red;
  font-size: 16px;
  margin-top: 10px;
}
</style>
