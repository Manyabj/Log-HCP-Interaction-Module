import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { sendChatMessage } from "../../services/api";

// This thunk is the single entry point for ALL form updates.
// The user never edits the form directly — every change flows through
// this AI chat call, whose response updates both chatSlice and
// interactionSlice (see interactionSlice's extraReducers).
export const sendMessage = createAsyncThunk(
  "chat/sendMessage",
  async ({ sessionId, message }, { rejectWithValue }) => {
    try {
      const data = await sendChatMessage(sessionId, message);
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || "Failed to reach AI assistant");
    }
  }
);

const initialState = {
  messages: [], // { role: "user" | "assistant", content: string }
  loading: false,
  error: null,
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    addLocalUserMessage(state, action) {
      state.messages.push({ role: "user", content: action.payload });
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.loading = false;
        state.messages = action.payload.history;
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { addLocalUserMessage } = chatSlice.actions;
export default chatSlice.reducer;
