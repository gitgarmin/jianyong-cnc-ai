import { Box, Typography, Paper, Card, CardContent, List, ListItemButton, ListItemText, Divider } from '@mui/material';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

export default function ProfileTab() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', p: 2, overflow: 'auto' }}>
      {/* 头像区 */}
      <Card sx={{ mb: 2 }}>
        <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: '50%',
              bgcolor: 'primary.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontSize: '1.5rem',
              fontWeight: 700,
            }}
          >
            操
          </Box>
          <Box>
            <Typography variant="h6">操作工</Typography>
            <Typography variant="body2" color="text.secondary">
              未认证工厂 · 操作员
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* 数据卡片 */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        {[
          { label: '本月提问', value: '0' },
          { label: '收藏方案', value: '0' },
          { label: '绑定机床', value: '0' },
        ].map((item) => (
          <Paper key={item.label} variant="outlined" sx={{ flex: 1, p: 1.5, textAlign: 'center' }}>
            <Typography variant="h5" color="primary" fontWeight={600}>
              {item.value}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {item.label}
            </Typography>
          </Paper>
        ))}
      </Box>

      {/* 我的套餐 */}
      <Card sx={{ mb: 2, bgcolor: 'primary.50' }}>
        <CardContent>
          <Typography variant="subtitle2" color="primary" gutterBottom>
            当前套餐
          </Typography>
          <Typography variant="body1" fontWeight={600}>
            体验版 · 免费试用中
          </Typography>
          <Typography variant="caption" color="text.secondary">
            剩余 30 天
          </Typography>
        </CardContent>
      </Card>

      {/* 功能入口 */}
      <Paper variant="outlined">
        <List disablePadding>
          <ListItemButton>
            <ListItemText primary="问答记录" secondary="查看最近对话" />
            <ChevronRightIcon color="action" />
          </ListItemButton>
          <Divider />
          <ListItemButton>
            <ListItemText primary="问题反馈" secondary="功能异常/知识库不准/建议" />
            <ChevronRightIcon color="action" />
          </ListItemButton>
          <Divider />
          <ListItemButton>
            <ListItemText primary="工厂认证" secondary="认证后解锁完整功能" />
            <ChevronRightIcon color="action" />
          </ListItemButton>
          <Divider />
          <ListItemButton>
            <ListItemText primary="关于" secondary="简用 数控AI大师 v0.1" />
            <ChevronRightIcon color="action" />
          </ListItemButton>
        </List>
      </Paper>
    </Box>
  );
}
