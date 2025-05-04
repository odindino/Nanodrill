#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SPM .int 檔案繪圖工具 - 簡易版

此腳本用於快速讀取和顯示 .int 檔案的內容。
使用方式：
    python int_plot.py 檔案路徑.int

範例：
    python int_plot.py data/sample.int
"""

import os
import sys
import numpy as np
import struct
import re
import plotly.graph_objects as go
import plotly.io as pio

# 設置顯示模式為瀏覽器
pio.renderers.default = "browser"

def parse_int_file(file_path, scale=1.0, x_pixel=512, y_pixel=512):
    """解析 .int 檔案並返回數據數組"""
    with open(file_path, 'rb') as f:
        int_file = f.read()
    
    image_data = []
    
    # 解析數據
    for i in range(int(len(int_file) / 4)):
        image_data_numvalue = struct.unpack('<i', int_file[4*i:4*i+4])[0]
        image_data.append(image_data_numvalue)
    
    # 轉換為 numpy 數組並重塑
    image_data = np.array(image_data)
    image_data = image_data.reshape(y_pixel, x_pixel)
    
    # 應用比例因子
    image_data = image_data * scale
    
    return image_data

def find_txt_file(int_file_path):
    """尋找對應的 .txt 檔案"""
    int_dir = os.path.dirname(int_file_path)
    int_basename = os.path.basename(int_file_path)
    
    # 嘗試從 int 檔名找出基本名稱
    match = re.search(r'(.+?)_(\d+)([^_]*?)\.(int)$', int_basename, re.IGNORECASE)
    if match:
        prefix = match.group(1)
        number = match.group(2)
        
        # 在同一目錄中尋找可能的 txt 檔案
        for filename in os.listdir(int_dir if int_dir else '.'):
            if filename.endswith('.txt') and filename.startswith(f"{prefix}_{number}"):
                return os.path.join(int_dir if int_dir else '.', filename)
    
    return None

def parse_txt_parameters(txt_file_path, int_file_basename):
    """從 txt 檔案解析參數"""
    params = {
        'scale': 1.0,
        'x_pixels': 512,
        'y_pixels': 512,
        'x_range': 100.0,
        'y_range': 100.0,
        'phys_unit': 'nm'
    }
    
    if not txt_file_path or not os.path.exists(txt_file_path):
        return params
    
    try:
        with open(txt_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 解析基本參數
        # 像素數
        x_pixel_match = re.search(r'xPixel\s*:\s*([^\n]+)', content)
        if x_pixel_match:
            try:
                params['x_pixels'] = int(x_pixel_match.group(1).strip())
            except ValueError:
                pass
        
        y_pixel_match = re.search(r'yPixel\s*:\s*([^\n]+)', content)
        if y_pixel_match:
            try:
                params['y_pixels'] = int(y_pixel_match.group(1).strip())
            except ValueError:
                pass
        
        # 掃描範圍
        x_range_match = re.search(r'XScanRange\s*:\s*([^\n]+)', content)
        if x_range_match:
            try:
                params['x_range'] = float(x_range_match.group(1).strip())
            except ValueError:
                pass
        
        y_range_match = re.search(r'YScanRange\s*:\s*([^\n]+)', content)
        if y_range_match:
            try:
                params['y_range'] = float(y_range_match.group(1).strip())
            except ValueError:
                pass
        
        # 物理單位
        x_unit_match = re.search(r'XPhysUnit\s*:\s*([^\n]+)', content)
        if x_unit_match:
            params['phys_unit'] = x_unit_match.group(1).strip()
        
        # 解析檔案描述區段以尋找 scale
        file_desc_pattern = r'FileDescBegin(.*?)FileDescEnd'
        file_descs = re.findall(file_desc_pattern, content, re.DOTALL)
        
        for desc_content in file_descs:
            filename_match = re.search(r'FileName\s*:\s*([^\n]+)', desc_content)
            if filename_match and filename_match.group(1).strip() == int_file_basename:
                scale_match = re.search(r'Scale\s*:\s*([^\n]+)', desc_content)
                if scale_match:
                    try:
                        params['scale'] = float(scale_match.group(1).strip())
                    except ValueError:
                        pass
                
                unit_match = re.search(r'PhysUnit\s*:\s*([^\n]+)', desc_content)
                if unit_match:
                    params['phys_unit'] = unit_match.group(1).strip()
    
    except Exception as e:
        print(f"解析 txt 檔案時出錯: {str(e)}")
    
    return params

def plot_topo_image(image_data, title="Topography", x_range=None, y_range=None, phys_unit="nm", colormap="Viridis"):
    """繪製形貌圖"""
    # 獲取數據尺寸
    y_size, x_size = image_data.shape
    
    # 如果提供了掃描範圍，創建對應的坐標軸
    if x_range is not None and y_range is not None:
        x = np.linspace(0, x_range, x_size)
        y = np.linspace(0, y_range, y_size)
    else:
        x = np.arange(x_size)
        y = np.arange(y_size)
    
    # 創建heatmap圖
    fig = go.Figure(data=go.Heatmap(
        z=image_data,
        x=x,
        y=y,
        colorscale=colormap,
        colorbar=dict(
            title=f'Height ({phys_unit})',
            titleside='right',
            titlefont=dict(size=14)
        )
    ))
    
    # 基本統計數據
    min_val = np.min(image_data)
    max_val = np.max(image_data)
    mean_val = np.mean(image_data)
    std_val = np.std(image_data)
    rms_val = np.sqrt(np.mean(np.square(image_data - mean_val)))
    
    # 設置佈局
    fig.update_layout(
        title=title,
        xaxis_title=f'X ({phys_unit})',
        yaxis_title=f'Y ({phys_unit})',
        xaxis=dict(
            scaleanchor="y",
            constrain='domain'
        ),
        autosize=True,
        width=700,
        height=600,
        margin=dict(l=65, r=50, t=90, b=65)
    )
    
    # 添加統計信息
    stat_text = (f"Min: {min_val:.2f} {phys_unit}, Max: {max_val:.2f} {phys_unit}, "
                f"Mean: {mean_val:.2f} {phys_unit}, RMS: {rms_val:.2f} {phys_unit}")
    
    fig.add_annotation(
        x=0.5,
        y=1.05,
        xref="paper",
        yref="paper",
        text=stat_text,
        showarrow=False,
        font=dict(size=12),
        align="center",
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="gray",
        borderwidth=1,
        borderpad=4
    )
    
    return fig

def linewise_flatten_mean(image_data):
    """按行減去均值進行平面化"""
    result = image_data.copy()
    for i in range(len(result)):
        result[i] -= np.mean(result[i])
    return result

def main():
    # 檢查命令行參數
    if len(sys.argv) < 2:
        print("使用方式: python int_plot.py 檔案路徑.int [flatten]")
        sys.exit(1)
    
    int_file_path = sys.argv[1]
    use_flatten = False
    
    if len(sys.argv) > 2 and sys.argv[2].lower() == 'flatten':
        use_flatten = True
    
    # 檢查檔案是否存在
    if not os.path.exists(int_file_path):
        print(f"錯誤: 檔案不存在 - {int_file_path}")
        sys.exit(1)
    
    # 尋找對應的 txt 檔案
    txt_file_path = find_txt_file(int_file_path)
    if txt_file_path:
        print(f"找到對應的 txt 檔案: {txt_file_path}")
    else:
        print("未找到對應的 txt 檔案，將使用預設參數")
    
    # 解析參數
    int_file_basename = os.path.basename(int_file_path)
    params = parse_txt_parameters(txt_file_path, int_file_basename)
    
    print(f"使用參數: scale={params['scale']}, "
          f"x_pixels={params['x_pixels']}, y_pixels={params['y_pixels']}, "
          f"x_range={params['x_range']}, y_range={params['y_range']}, "
          f"phys_unit={params['phys_unit']}")
    
    try:
        # 解析 .int 檔案
        image_data = parse_int_file(
            int_file_path, 
            params['scale'], 
            params['x_pixels'], 
            params['y_pixels']
        )
        
        # 檔案基本名稱 (不含路徑和副檔名)
        base_name = os.path.splitext(os.path.basename(int_file_path))[0]
        
        # 如果需要平面化
        if use_flatten:
            print("應用平面化處理...")
            image_data = linewise_flatten_mean(image_data)
        
        # 繪製圖像
        fig = plot_topo_image(
            image_data,
            title=base_name,
            x_range=params['x_range'],
            y_range=params['y_range'],
            phys_unit=params['phys_unit']
        )
        
        # 顯示圖像
        fig.show()
        
    except Exception as e:
        print(f"處理 .int 檔案時出錯: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()