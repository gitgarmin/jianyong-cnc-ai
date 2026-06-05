import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { BottomNavigation, BottomNavigationAction, Paper, Box, AppBar, Toolbar, Typography, Chip } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import CodeIcon from '@mui/icons-material/Code';
import PersonIcon from '@mui/icons-material/Person';
import { useAppStore } from '../../stores/appStore';

const NAV_ITEMS = [
  { path: '/chat', label: '对话问答', icon: <ChatIcon /> },
  { path: '/gcode', label: 'G代码', icon: <CodeIcon /> },
  { path: '/profile', label: '我的', icon: <PersonIcon /> },
];

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [value, setValue] = useState(() => {
    const match = NAV_ITEMS.find((item) => location.pathname.startsWith(item.path));
    return match ? match.path : '/chat';
  });

  const { globalStatus } = useAppStore();

  const handleChange = (_: React.SyntheticEvent, newValue: string) => {
    setValue(newValue);
    navigate(newValue);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100dvh', bgcolor: 'background.default' }}>
      {/* 全局状态条 */}
      {globalStatus && (
        <AppBar position="static" color="primary" elevation={0} sx={{ bgcolor: '#1565c0' }}>
          <Toolbar variant="dense" sx={{ minHeight: 40, px: 2, gap: 1 }}>
            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
              {globalStatus}
            </Typography>
            {globalStatus.includes('步骤 2') && (
              <Chip label="跳转到步骤1" size="small" color="default" variant="outlined" sx={{ color: '#fff', borderColor: '#fff' }} />
            )}
          </Toolbar>
        </AppBar>
      )}

      {/* 页面内容 */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <Outlet />
      </Box>

      {/* 底部导航 */}
      <Paper elevation={3} sx={{ position: 'sticky', bottom: 0 }}>
        <BottomNavigation value={value} onChange={handleChange} showLabels>
          {NAV_ITEMS.map((item) => (
            <BottomNavigationAction key={item.path} value={item.path} label={item.label} icon={item.icon} />
          ))}
        </BottomNavigation>
      </Paper>
    </Box>
  );
}
