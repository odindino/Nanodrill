// src/stores/userPreferencesStore.ts
import { defineStore } from 'pinia';

interface UserPreferences {
  fileSelectorWidth: number;
  columnWidths: {
    [key: string]: number;
  };
  sortOption: string;
  lastDirectory?: string;
}

// 使用 localStorage 儲存和讀取使用者偏好
const STORAGE_KEY = 'nanodrill_user_preferences';

// 預設偏好設定
const DEFAULT_PREFERENCES: UserPreferences = {
  fileSelectorWidth: 450,
  columnWidths: {
    filename: 280,
    time: 150
  },
  sortOption: 'time_desc'
};

// 從 localStorage 讀取偏好設定
const loadPreferences = (): UserPreferences => {
  try {
    const savedPreferences = localStorage.getItem(STORAGE_KEY);
    if (savedPreferences) {
      return JSON.parse(savedPreferences);
    }
  } catch (error) {
    console.error('Failed to load preferences from localStorage:', error);
  }
  return DEFAULT_PREFERENCES;
};

// 將偏好設定儲存到 localStorage
const savePreferences = (preferences: UserPreferences): void => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
  } catch (error) {
    console.error('Failed to save preferences to localStorage:', error);
  }
};

export const useUserPreferencesStore = defineStore('userPreferences', {
  state: () => loadPreferences(),
  
  actions: {
    // 更新選擇器寬度
    setFileSelectorWidth(width: number) {
      this.fileSelectorWidth = width;
      savePreferences(this.$state);
    },
    
    // 更新欄位寬度
    setColumnWidth(columnKey: string, width: number) {
      this.columnWidths[columnKey] = width;
      savePreferences(this.$state);
    },
    
    // 更新排序選項
    setSortOption(option: string) {
      this.sortOption = option;
      savePreferences(this.$state);
    },
    
    // 更新上次開啟的目錄
    setLastDirectory(directory: string) {
      this.lastDirectory = directory;
      savePreferences(this.$state);
    },
    
    // 重設為預設值
    resetToDefaults() {
      const defaultPrefs = { ...DEFAULT_PREFERENCES };
      this.$patch(defaultPrefs);
      savePreferences(this.$state);
    }
  }
});