import { Box, Typography, TextField, IconButton, Paper, Chip, Stack } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import PhotoCameraIcon from '@mui/icons-material/PhotoCamera';
import KeyboardVoiceIcon from '@mui/icons-material/KeyboardVoice';
import { useState } from 'react';
import { sendChatMessage } from '../../lib/api';

const QUICK_TAGS = ['工件振纹怎么调', '45#钢粗车参数', 'FANUC报警PS0010', '不锈钢表面粗糙度'];

export default function ChatTab() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages([...messages, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await sendChatMessage(input);
      setMessages(prev => [...prev, { role: 'assistant', content: res.reply }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'AI服务暂时不可用' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', p: 2 }}>
      <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 0.5 }}>
        {QUICK_TAGS.map((tag) => (
          <Chip key={tag} label={tag} variant="outlined" onClick={() => setInput(tag)} clickable />
        ))}
      </Stack>

      <Paper
        variant="outlined"
        sx={{ flex: 1, mb: 2, p: 2, overflow: 'auto', bgcolor: 'grey.50' }}
      >
        {messages.map((msg, idx) => (
          <Box key={idx} sx={{ mb: 2, textAlign: msg.role === 'user' ? 'right' : 'left' }}>
            <Paper
              elevation={0}
              sx={{
                p: 1.5,
                display: 'inline-block',
                maxWidth: '80%',
                bgcolor: msg.role === 'user' ? 'primary.main' : 'background.paper',
                color: msg.role === 'user' ? 'white' : 'text.primary',
                borderRadius: msg.role === 'user' ? '12px 12px 0 12px' : '12px 12px 12px 0',
              }}
            >
              <Typography variant="body2">{msg.content}</Typography>
            </Paper>
          </Box>
        ))}
        {loading && (
          <Typography variant="body2" color="text.secondary">思考中...</Typography>
        )}
      </Paper>

      <Paper elevation={2} sx={{ p: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
        <IconButton size="small" color="primary"><PhotoCameraIcon /></IconButton>
        <TextField
          fullWidth size="small" placeholder="输入加工问题..." variant="outlined"
          value={input} onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') handleSend(); }}
          sx={{ '& fieldset': { border: 'none' } }}
        />
        <IconButton size="small" color="primary"><KeyboardVoiceIcon /></IconButton>
        <IconButton size="small" color="primary" onClick={handleSend} disabled={!input.trim()} data-testid="send-button">
          <SendIcon />
        </IconButton>
      </Paper>
    </Box>
  );
}
