import { Routes, Route, Navigate } from "react-router-dom";
import LogInteraction from "./pages/LogInteraction/LogInteraction";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/log-interaction" replace />} />
      <Route path="/log-interaction" element={<LogInteraction />} />
    </Routes>
  );
}
