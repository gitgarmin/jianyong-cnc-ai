import { create } from 'zustand';

interface AppState {
  /**
   * 全局状态条文字，如 "📄 零件A-v2.dxf | 步骤2/4 图纸解析"
   * null 时不显示状态条
   */
  globalStatus: string | null;
  setGlobalStatus: (status: string | null) => void;

  /**
   * G代码流程的跨Tab上下文：从G代码跳转对话时自动注入
   */
  workpieceContext: string | null;
  setWorkpieceContext: (ctx: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  globalStatus: null,
  setGlobalStatus: (globalStatus) => set({ globalStatus }),
  workpieceContext: null,
  setWorkpieceContext: (workpieceContext) => set({ workpieceContext }),
}));
