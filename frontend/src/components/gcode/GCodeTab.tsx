import { Box, Typography, Paper, Stepper, Step, StepLabel, Button } from '@mui/material';
import { useState } from 'react';
import { useAppStore } from '../../stores/appStore';

const STEPS = ['上传图纸与选择', '图纸解析与确认', 'G代码输出与安全确认', '首件检验与刀具管理'];

export default function GCodeTab() {
  const [activeStep, setActiveStep] = useState(0);
  const { setGlobalStatus } = useAppStore();

  const handleNext = () => {
    const nextStep = activeStep + 1;
    setActiveStep(nextStep);
    setGlobalStatus(`📄 未命名零件 | 步骤${nextStep + 1}/${STEPS.length} ${STEPS[nextStep]}`);
  };

  const handleReset = () => {
    setActiveStep(0);
    setGlobalStatus(null);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', p: 2 }}>
      {/* 步骤指示器 */}
      <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 3 }}>
        {STEPS.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* 步骤内容（占位） */}
      <Paper
        variant="outlined"
        sx={{
          flex: 1,
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'grey.50',
        }}
      >
        <Typography variant="h6" color="text.secondary" gutterBottom>
          {STEPS[activeStep]}
        </Typography>
        <Typography variant="body2" color="text.disabled" align="center" sx={{ maxWidth: 400 }}>
          {activeStep === 0 && '上传毛坯图纸和成品图纸，选择材质和机床型号'}
          {activeStep === 1 && 'AI 将解析图纸提取尺寸公差，支持逐项编辑确认'}
          {activeStep === 2 && '安全校验引擎检查 G 代码，28 条规则三级校验'}
          {activeStep === 3 && '生成首件检验清单，AI 辅助判定合格/不合格'}
        </Typography>
      </Paper>

      {/* 操作按钮 */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
        <Button variant="outlined" onClick={handleReset} disabled={activeStep === 0}>
          重新开始
        </Button>
        <Button variant="contained" onClick={handleNext} disabled={activeStep >= STEPS.length - 1}>
          {activeStep >= STEPS.length - 1 ? '已完成全部步骤' : '下一步（模拟）'}
        </Button>
      </Box>
    </Box>
  );
}
