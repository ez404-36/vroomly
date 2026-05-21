import { createSlice } from '@reduxjs/toolkit';

interface LayoutState {
  leftSidebarOpen: boolean;
  rightSidebarOpen: boolean;
}

const STORAGE_KEY = 'layout-preferences';

function loadFromStorage(): Partial<LayoutState> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      return JSON.parse(raw) as Partial<LayoutState>;
    }
  } catch {
    /* ignore corrupt data */
  }
  return {};
}

function persist(state: LayoutState): void {
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      leftSidebarOpen: state.leftSidebarOpen,
      rightSidebarOpen: state.rightSidebarOpen,
    }),
  );
}

const saved = loadFromStorage();

const initialState: LayoutState = {
  leftSidebarOpen: saved.leftSidebarOpen ?? true,
  rightSidebarOpen: saved.rightSidebarOpen ?? false,
};

const layoutSlice = createSlice({
  name: 'layout',
  initialState,
  reducers: {
    toggleLeftSidebar(state) {
      state.leftSidebarOpen = !state.leftSidebarOpen;
      persist(state);
    },
    toggleRightSidebar(state) {
      state.rightSidebarOpen = !state.rightSidebarOpen;
      persist(state);
    },
    setLeftSidebar(state, action: { payload: boolean }) {
      state.leftSidebarOpen = action.payload;
      persist(state);
    },
    setRightSidebar(state, action: { payload: boolean }) {
      state.rightSidebarOpen = action.payload;
      persist(state);
    },
  },
});

export const {
  toggleLeftSidebar,
  toggleRightSidebar,
  setLeftSidebar,
  setRightSidebar,
} = layoutSlice.actions;
export default layoutSlice.reducer;
