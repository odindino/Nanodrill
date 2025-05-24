#!/usr/bin/env python3
"""
測試增強的色彩映射系統
驗證新的 get_plotly_colorscale 函數是否能正確處理各種 matplotlib 色彩映射
"""

import sys
import os
import numpy as np

# 添加 backend 路徑到 Python 路徑
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

from core.analysis.int_analysis import IntAnalysis

def test_colormap_function():
    """測試色彩映射函數"""
    
    print("=== 測試 matplotlib 色彩映射系統 ===\n")
    
    # 測試常用的 matplotlib 色彩映射
    test_colormaps = [
        'viridis',       # 流行的科學色彩映射
        'plasma',        # 另一個流行的選擇
        'inferno',       # 暖色調
        'magma',         # 暗色調
        'cividis',       # 色盲友好
        'Greys',         # 灰階
        'Blues',         # 藍色系（原有的自定義映射）
        'Oranges',       # 橘色系（原有的自定義映射）
        'Reds',          # 紅色系
        'coolwarm',      # 冷暖色調
        'RdYlBu',        # 紅-黃-藍
        'Spectral',      # 光譜色
        'viridis_r',     # 測試反轉映射
        'plasma_r',      # 測試反轉映射
        'invalid_cmap',  # 測試無效映射
    ]
    
    success_count = 0
    total_tests = len(test_colormaps)
    
    for colormap_name in test_colormaps:
        try:
            print(f"測試色彩映射: {colormap_name}")
            result = IntAnalysis.get_plotly_colorscale(colormap_name)
            
            if isinstance(result, list):
                # 檢查返回的格式是否正確
                if len(result) > 0 and isinstance(result[0], list) and len(result[0]) == 2:
                    print(f"  ✓ 成功生成色彩陣列，包含 {len(result)} 個色彩點")
                    print(f"  範例色彩點: {result[0]} 到 {result[-1]}")
                    success_count += 1
                else:
                    print(f"  ✗ 返回格式錯誤: {type(result)}")
            elif isinstance(result, str):
                print(f"  ✓ 返回 Plotly 內建映射: {result}")
                success_count += 1
            else:
                print(f"  ✗ 未知返回類型: {type(result)}")
                
        except Exception as e:
            print(f"  ✗ 錯誤: {str(e)}")
        
        print()
    
    print(f"=== 測試結果 ===")
    print(f"成功: {success_count}/{total_tests}")
    print(f"成功率: {success_count/total_tests*100:.1f}%")
    
    return success_count == total_tests

def test_color_array_format():
    """測試色彩陣列格式"""
    print("\n=== 測試色彩陣列格式 ===\n")
    
    # 測試一個 matplotlib 色彩映射
    colormap_name = 'viridis'
    result = IntAnalysis.get_plotly_colorscale(colormap_name)
    
    if isinstance(result, list):
        print(f"色彩陣列長度: {len(result)}")
        print(f"第一個元素: {result[0]}")
        print(f"最後一個元素: {result[-1]}")
        
        # 檢查每個元素的格式
        for i, color_point in enumerate(result[:5]):  # 只檢查前5個
            position, color = color_point
            print(f"色彩點 {i}: 位置={position:.3f}, 顏色={color}")
            
            # 驗證位置值在 0-1 範圍內
            if not (0 <= position <= 1):
                print(f"  ✗ 位置值超出範圍: {position}")
                return False
                
            # 驗證顏色是十六進制格式
            if not (isinstance(color, str) and color.startswith('#') and len(color) == 7):
                print(f"  ✗ 顏色格式錯誤: {color}")
                return False
        
        print("✓ 色彩陣列格式正確")
        return True
    else:
        print(f"✗ 預期返回列表，實際返回: {type(result)}")
        return False

def test_reverse_mapping():
    """測試反轉映射功能"""
    print("\n=== 測試反轉映射功能 ===\n")
    
    # 測試正常和反轉映射
    normal_map = IntAnalysis.get_plotly_colorscale('viridis')
    reversed_map = IntAnalysis.get_plotly_colorscale('viridis_r')
    
    if isinstance(normal_map, list) and isinstance(reversed_map, list):
        print(f"正常映射首色: {normal_map[0][1]}")
        print(f"正常映射尾色: {normal_map[-1][1]}")
        print(f"反轉映射首色: {reversed_map[0][1]}")
        print(f"反轉映射尾色: {reversed_map[-1][1]}")
        
        # 反轉映射的首色應該接近正常映射的尾色
        # 這裡只做簡單的檢查，確保它們不相同
        if normal_map[0][1] != reversed_map[0][1]:
            print("✓ 反轉映射功能正常")
            return True
        else:
            print("✗ 反轉映射與正常映射相同")
            return False
    else:
        print("✗ 無法比較映射類型")
        return False

if __name__ == "__main__":
    print("開始測試增強的色彩映射系統...\n")
    
    # 執行各項測試
    test1 = test_colormap_function()
    test2 = test_color_array_format()
    test3 = test_reverse_mapping()
    
    print(f"\n=== 總體測試結果 ===")
    if test1 and test2 and test3:
        print("✓ 所有測試通過！色彩映射系統升級成功。")
    else:
        print("✗ 部分測試失敗，需要檢查實作。")
