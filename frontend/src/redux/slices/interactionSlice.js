import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { fetchInteraction, saveInteraction } from "../../services/api";
import { sendMessage } from "./chatSlice";

export const loadInteraction = createAsyncThunk(
  "interaction/load",
  async (sessionId, { rejectWithValue }) => {
    try {
      return await fetchInteraction(sessionId);
    } catch (err) {
      // 404 simply means nothing logged yet for this session — not an error.
      if (err.response?.status === 404) return null;
      return rejectWithValue(err.response?.data?.detail || "Failed to load interaction");
    }
  }
);

export const submitInteraction = createAsyncThunk(
  "interaction/save",
  async (sessionId, { rejectWithValue }) => {
    try {
      return await saveInteraction(sessionId);
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || "Failed to save interaction");
    }
  }
);

const emptyFields = {
  hcp_name: null,
  interaction_type: null,
  interaction_date: null,
  interaction_time: null,
  attendees: [],
  topics: [],
  product: null,
  sentiment: null,
  materials: [],
  notes: null,
  summary: null,
  status: "draft",
};

const initialState = {
  fields: emptyFields,
  isValidForSave: false,
  missingFields: [],
  lastToolUsed: null,
  loading: false,
  saving: false,
  saved: false,
  error: null,
};

const interactionSlice = createSlice({
  name: "interaction",
  initialState,
  reducers: {
    resetInteraction(state) {
      state.fields = emptyFields;
      state.isValidForSave = false;
      state.missingFields = [];
      state.saved = false;
    },
  },
  extraReducers: (builder) => {
    builder
      // Populated purely from the AI chat response — this is the ONLY
      // write-path for form data, per product requirement.
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.fields = action.payload.interaction;
        state.isValidForSave = action.payload.is_valid_for_save;
        state.missingFields = action.payload.missing_fields;
        state.lastToolUsed = action.payload.tool_used;
      })
      .addCase(loadInteraction.pending, (state) => {
        state.loading = true;
      })
      .addCase(loadInteraction.fulfilled, (state, action) => {
        state.loading = false;
        if (action.payload) {
          state.fields = action.payload;
        }
      })
      .addCase(loadInteraction.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(submitInteraction.pending, (state) => {
        state.saving = true;
        state.error = null;
      })
      .addCase(submitInteraction.fulfilled, (state, action) => {
        state.saving = false;
        state.saved = true;
        state.fields = action.payload;
      })
      .addCase(submitInteraction.rejected, (state, action) => {
        state.saving = false;
        state.error = action.payload;
      });
  },
});

export const { resetInteraction } = interactionSlice.actions;
export default interactionSlice.reducer;
