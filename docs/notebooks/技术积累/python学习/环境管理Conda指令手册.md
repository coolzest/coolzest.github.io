# Conda 日常全量指令手册
适配 Windows 系统，覆盖环境管理、包管理、镜像配置、问题排查，结合你的 PySide 项目场景，直接复制可用。

## 一、基础初始化操作
### 1. 环境变量修复（解决“conda 未识别”）
```powershell
# 临时生效（重启终端失效）
$env:Path += ";C:\Users\coolzest\miniconda3\Scripts"

# 永久生效（一键配置，无需手动改环境变量）
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
$newPath = $currentPath + ";C:\Users\coolzest\miniconda3\Scripts"
[Environment]::SetEnvironmentVariable("Path", $newPath, "User")
```

### 2. 验证conda安装
```powershell
conda --version  # 输出版本号即成功（如 conda 24.5.0）
conda info       # 查看conda详细信息（环境、路径、镜像源等）
```

## 二、镜像源配置（加速下载，解决超时）
### 1. 配置清华镜像源（推荐，国内优先）
```powershell
# 添加核心镜像源
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/msys2/

# 显示下载源（方便排查，可选）
conda config --set show_channel_urls yes

# 取消默认镜像源（避免冲突，可选）
conda config --remove-key channels defaults
```

### 2. 查看/重置镜像源
```powershell
conda config --show-sources  # 查看当前配置的镜像源
conda config --remove-key channels  # 重置为默认镜像源（无需时执行）
```

## 三、环境管理（核心功能，解决依赖冲突）
### 1. 环境创建
```powershell
# 创建指定Python版本的环境（示例：PySide项目专属环境）
conda create -n pyside_env python=3.11 -y  # -n 指定环境名，-y 自动确认

# 创建带依赖包的环境（一次性安装所需包）
conda create -n pyside_env python=3.11 pyside6 numpy=1.26 -y

# 从配置文件创建环境（团队协作/项目迁移用）
conda env create -f environment.yml  # 需提前准备yml文件
```

### 2. 环境激活/退出
```powershell
conda activate pyside_env  # 激活环境（每次运行项目前执行）
conda deactivate           # 退出当前环境
```

### 3. 环境查看/搜索
```powershell
conda env list             # 查看所有已创建的环境（*标注当前环境）
conda info --envs          # 同上，详细显示环境路径
```

### 4. 环境更新/复制
```powershell
# 更新环境中的Python版本（示例：更新到3.11.9）
conda install -n pyside_env python=3.11.9 -y

# 复制环境（基于现有环境创建新环境）
conda create -n pyside_env_copy --clone pyside_env -y
```

### 5. 环境删除（清理无用环境）
```powershell
conda env remove -n pyside_env -y  # 删除指定环境（谨慎操作）
```

## 四、包管理（安装/更新/卸载依赖）
### 1. 包安装
```powershell
# 激活环境后安装（推荐，仅当前环境生效）
conda activate pyside_env
conda install pyside6  # 安装最新版
conda install numpy=1.26  # 安装指定版本（解决版本冲突）
conda install pyside6 numpy pandas  # 同时安装多个包

# 不激活环境，直接给指定环境安装包
conda install -n pyside_env matplotlib -y
```

### 2. 包查看/搜索
```powershell
conda list                # 查看当前环境已安装的所有包
conda list numpy          # 查看指定包的版本（如numpy）
conda search numpy        # 搜索conda仓库中的可用包版本
```

### 3. 包更新/升级
```powershell
conda update numpy        # 更新指定包到最新版
conda update --all        # 更新当前环境所有包（谨慎，避免兼容性问题）
conda update conda        # 更新conda本身
```

### 4. 包卸载
```powershell
conda remove numpy -y     # 卸载当前环境中的指定包
conda remove -n pyside_env pandas -y  # 卸载指定环境的包
conda clean -p            # 清理未使用的包缓存（释放空间）
```

## 五、项目实战专用指令（你的PySide项目）
### 1. 一键搭建PySide环境
```powershell
# 1. 配置镜像源（已配置可跳过）
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --set show_channel_urls yes

# 2. 创建并激活环境
conda create -n pyside_env python=3.11 -y
conda activate pyside_env

# 3. 安装依赖（PySide6 + 兼容NumPy）
conda install pyside6 numpy=1.26 -y

# 4. 运行项目（替换为你的项目路径）
cd E:\Documents\VSCode_project
python main.py
```

### 2. 导出/导入项目环境（备份/分享）
```powershell
# 导出当前环境配置到yml文件（备份/给他人使用）
conda env export > environment.yml

# 他人导入你的环境（基于yml文件重建）
conda env create -f environment.yml -y
```

## 六、问题排查与清理指令
### 1. 解决“conda识别不到”
```powershell
# 检查conda安装路径是否正确
Test-Path "C:\Users\coolzest\miniconda3\Scripts\conda.exe"  # 返回True即路径正确

# 重新初始化conda（适用于终端无法激活环境）
conda init powershell  # 初始化PowerShell
conda init cmd         # 初始化CMD（如需使用CMD）
```

### 2. 清理缓存（解决下载失败/空间占用）
```powershell
conda clean -p    # 清理未使用的包
conda clean -t    # 清理包缓存（tarballs）
conda clean -y --all  # 清理所有缓存（彻底清理）
```

### 3. 修复损坏的环境
```powershell
conda clean --all -y  # 先清理缓存
conda env remove -n pyside_env -y  # 删除损坏环境
conda create -n pyside_env python=3.11 pyside6 numpy=1.26 -y  # 重新创建
```

## 七、常用快捷键组合（提高效率）
| 操作                | 指令组合                                  |
|---------------------|-------------------------------------------|
| 快速激活PySide环境  | `conda activate pyside_env`               |
| 一键更新所有依赖    | `conda activate pyside_env && conda update --all -y` |
| 备份环境+清理缓存   | `conda env export > environment.yml && conda clean -y --all` |

