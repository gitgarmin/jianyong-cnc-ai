import { Box, Typography, TextField, IconButton, Paper, Chip, Stack } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import KeyboardVoiceIcon from '@mui/icons-material/KeyboardVoice';
import { useState } from 'react';

const QUICK_TAGS = ['工件振纹怎么调', '45#钢粗车参数', 'FANUC报警PS0010', '不锈钢表面粗糙度'];

export default function ChatTab() {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (!input.trim()) return;
    // TODO: 对接后端 AI 问答接口
    setInput('');
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', p: 2 }}>
      {/* 快捷提问标签 */}
      <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 0.5 }}>
        {QUICK_TAGS.map((tag) => (
          <Chip key={tag} label={tag} variant="outlined" onClick={() => setInput(tag)} clickable />
        ))}
      </Stack>

      {/* 对话区域（占位） */}
      <Paper
        variant="outlined"
        sx={{
          flex: 1,
          mb: 2,
          p: 3,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'grey.50',
        }}
      >
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            AI 对话问答
          </Typography>
          <Typography variant="body2" color="text.disabled">
            描述加工问题或上传工件照片，AI 将基于知识库为你诊断和推荐方案
          </Typography>
          <Typography variant="caption" color="text.disabled" sx={{ mt: 1, display: 'block' }}>
            支持文字 + 图片 + 语音输入
          </Typography>
        </Box>
      </Paper>

      {/* 输入区域 */}
      <Paper elevation={2} sx={{ p: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
        <IconButton size="small" color="primary">
          <PhotoCameraIcon />
        </IconButton>
        <TextField
          fullWidth
          size="small"
          placeholder="输入加工问题..."
          variant="outlined"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') handleSend(); }}
          sx={{ '& fieldset': { border: 'none' } }}
        />
        <IconButton size="small" color="primary">
          <KeyboardVoiceIcon />
        </IconButton>
        <IconButton size="small" color="primary" onClick={handleSend} disabled={!input.trim()}>
          <SendIcon />
        </IconButton>
      </Paper>
    </Box>
  );
}
