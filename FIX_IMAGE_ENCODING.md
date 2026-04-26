# ✅ 图片乱码问题已修复

**修复时间**: 2026年4月26日 23:20  
**问题**: matplotlib 中文字符显示为方框  
**解决方案**: 使用英文标签 + 配置字体支持  

---

## 🔧 修复内容

### 1. 添加字体配置

在脚本开头添加了 matplotlib 字体配置：

```python
import matplotlib

# 设置中文字体支持
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False
```

### 2. 修改图表标签为英文

将所有中文标签改为英文，避免字体兼容性问题：

#### 图1: 收盘价走势
- ❌ 之前: `'预测收盘价'`, `'当前价格'`, `'价格区间'`, `'价格 (¥)'`
- ✅ 现在: `'Predicted Close'`, `'Current Price'`, `'Price Range'`, `'Price (¥)'`

#### 图2: 成交量
- ❌ 之前: `'成交量'`
- ✅ 现在: `'Volume'`

#### 图3: 累计收益率
- ❌ 之前: `'累计收益率 (%)'`, `'时间'`
- ✅ 现在: `'Cumulative Return (%)'`, `'Time'`

---

## 📊 新旧对比

### 旧图片 (有乱码)
```
文件: ths_300033_5min_3days_pred_20260426_231342.png
大小: 183 KB
状态: ⚠️  中文字符显示为方框
警告: Glyph XXXXX missing from font(s) DejaVu Sans
```

### 新图片 (已修复)
```
文件: ths_300033_5min_3days_pred_20260426_232025.png
大小: 187 KB
状态: ✅ 所有字符正常显示
警告: 无
```

---

## 🎨 图表说明

### 三子图布局

```
┌─────────────────────────────────────┐
│  THS 300033 - 3-Day 5-Min Prediction │
│                                     │
│  Predicted Close                    │
│  Current Price ¥228.52              │
│  Price Range                        │
│                                     │
│  Price (¥)                          │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│                                     │
│  Volume                             │
│                                     │
│  Volume                             │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│                                     │
│  Cumulative Return (%)              │
│                                     │
│  Time                               │
└─────────────────────────────────────┘
```

### 颜色方案

- **蓝色 (#2E86AB)**: 上涨/正向
- **紫色 (#A23B72)**: 下跌/负向
- **橙色 (#F18F01)**: 累计收益
- **红色虚线**: 当前价格参考线

---

## 💡 最佳实践

### 方案选择

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **英文标签** | 通用性好，无依赖 | 需要翻译 | ⭐⭐⭐⭐⭐ |
| **中文字体** | 保持中文 | 需要安装字体 | ⭐⭐⭐ |
| **混合方案** | 灵活 | 复杂度高 | ⭐⭐⭐⭐ |

**本次采用**: 英文标签方案（最可靠）

### macOS 字体配置

如果需要使用中文，可以配置以下字体：

```python
# macOS 推荐字体
matplotlib.rcParams['font.sans-serif'] = [
    'Arial Unicode MS',  # macOS 自带
    'PingFang SC',       # macOS 苹方
    'STHeiti',           # 黑体
    'SimHei'             # 中易黑体
]
```

### Linux 字体配置

```python
# Linux 需要先安装字体
# sudo apt-get install fonts-wqy-zenhei

matplotlib.rcParams['font.sans-serif'] = [
    'WenQuanYi Zen Hei',  # 文泉驿正黑
    'Droid Sans Fallback'
]
```

### Windows 字体配置

```python
matplotlib.rcParams['font.sans-serif'] = [
    'SimHei',      # 中易黑体
    'Microsoft YaHei',  # 微软雅黑
    'KaiTi'        # 楷体
]
```

---

## 🔍 验证方法

### 检查是否有乱码警告

运行脚本时观察输出：

```bash
python finetune/predict_300033_5min_3days.py 2>&1 | grep "Glyph"
```

- ✅ **无输出**: 没有乱码
- ❌ **有输出**: 仍有乱码问题

### 查看图片

```bash
# macOS 预览
open outputs/predictions/ths_300033_5min_3days_pred_*.png

# Linux
xdg-open outputs/predictions/ths_300033_5min_3days_pred_*.png

# Windows
start outputs/predictions/ths_300033_5min_3days_pred_*.png
```

---

## 📝 其他建议

### 1. 统一使用英文

对于国际化项目，建议：
- ✅ 代码中使用英文注释和标签
- ✅ 文档提供中英文版本
- ✅ 图表使用英文标签

### 2. 字体回退机制

```python
import platform

system = platform.system()

if system == 'Darwin':  # macOS
    fonts = ['Arial Unicode MS', 'PingFang SC']
elif system == 'Linux':
    fonts = ['WenQuanYi Zen Hei']
elif system == 'Windows':
    fonts = ['SimHei', 'Microsoft YaHei']
else:
    fonts = ['DejaVu Sans']

matplotlib.rcParams['font.sans-serif'] = fonts
```

### 3. 保存多种格式

```python
# 同时保存 PNG 和 PDF
plt.savefig('chart.png', dpi=150, bbox_inches='tight')
plt.savefig('chart.pdf', bbox_inches='tight')  # PDF 矢量图
```

---

## ✅ 修复结果

### 修复前
```
⚠️  UserWarning: Glyph 38388 (\N{CJK UNIFIED IDEOGRAPH-95F4}) missing from font(s) DejaVu Sans.
⚠️  UserWarning: Glyph 25104 (\N{CJK UNIFIED IDEOGRAPH-6210}) missing from font(s) DejaVu Sans.
...
[大量警告信息]
```

### 修复后
```
✅ 无警告
✅ 所有文本正常显示
✅ 图片清晰美观
```

---

## 🎯 总结

### 问题根源
- matplotlib 默认字体 (DejaVu Sans) 不支持中文字符
- macOS 环境下字体配置需要特别处理

### 解决方案
1. 添加字体配置（备选方案）
2. 使用英文标签（主要方案）✅

### 效果
- ✅ 无乱码警告
- ✅ 跨平台兼容性好
- ✅ 无需额外字体安装
- ✅ 代码更简洁

---

**修复完成！新图片已生成，所有文本正常显示！** 🎉

---

*修复时间: 2026年4月26日 23:20*  
*修复方法: 英文标签 + 字体配置*  
*验证状态: ✅ 通过*
