import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import ChatTab from './components/chat/ChatTab';
import GCodeTab from './components/gcode/GCodeTab';
import ProfileTab from './components/profile/ProfileTab';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/chat" replace />} />
        <Route path="/chat" element={<ChatTab />} />
        <Route path="/gcode" element={<GCodeTab />} />
        <Route path="/profile" element={<ProfileTab />} />
      </Route>
    </Routes>
  );
}
