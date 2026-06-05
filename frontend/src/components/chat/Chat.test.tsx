import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatTab from './ChatTab';
import { sendChatMessage } from '../../lib/api';

// Mock API
vi.mock('../../lib/api', () => ({
  sendChatMessage: vi.fn(),
}));

describe('ChatTab', () => {
  it('renders input and send button', () => {
    render(<ChatTab />);
    expect(screen.getByPlaceholderText('输入加工问题...')).toBeInTheDocument();
    expect(screen.getByTestId('send-button')).toBeInTheDocument();
  });

  it('sends message and displays reply', async () => {
    const mockReply = { reply: '建议将转速调整至 S1200' };
    (sendChatMessage as any).mockResolvedValue(mockReply);

    render(<ChatTab />);

    const input = screen.getByPlaceholderText('输入加工问题...');
    fireEvent.change(input, { target: { value: '45#钢粗车参数' } });

    const sendBtn = screen.getByTestId('send-button');
    fireEvent.click(sendBtn);

    await waitFor(() => {
      expect(sendChatMessage).toHaveBeenCalledWith('45#钢粗车参数');
      expect(screen.getByText('建议将转速调整至 S1200')).toBeInTheDocument();
    });
  });
});
