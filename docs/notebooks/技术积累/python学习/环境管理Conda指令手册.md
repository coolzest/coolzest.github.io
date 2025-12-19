# Conda 个人速查手册（Windows版）


## 一、基础初始化（解决conda未识别/验证安装）
| 功能                 | 指令                                                                 |
|----------------------|----------------------------------------------------------------------|
| 临时添加conda路径    | `$env:Path += ";C:\Users\coolzest\miniconda3\Scripts"`                |
| 永久配置conda路径    | `$currentPath = [Environment]::GetEnvironmentVariable("Path", "User"); $newPath = $currentPath + ";C:\Users\coolzest\miniconda3\Scripts"; [Environment]::SetEnvironmentVariable("Path", $newPath, "User")` |
| 验证conda版本        | `conda --version`                                                    |
| 查看conda详细信息    | `conda info`                                                         |
| 初始化PowerShell     | `conda init powershell`                                              |
| 初始化CMD            | `conda init cmd`                                                     |

## 二、环境管理（核心操作，适配个人环境）
| 功能                 | 指令                                                                 |
|----------------------|----------------------------------------------------------------------|
| 查看所有环境         | `conda env list`                                                     |
| 查看环境详细路径     | `conda info --envs`                                                  |
| 激活base环境         | `conda activate base`                                                |
| 激活daily-env环境    | `conda activate daily-env`                                           |
| 激活daily_dev环境    | `conda activate daily_dev`                                           |
| 激活mkdocs-env环境   | `conda activate mkdocs-env`                                          |
| 激活qtpy-env环境     | `conda activate qtpy-env`                                            |
| 激活test_env环境     | `conda activate test_env`                                            |
| 退出当前环境         | `conda deactivate`                                                   |
| 创建daily-env（Python3.11） | `conda create -n daily-env python=3.11 -y`                        |
| 创建qtpy-env（带PySide6） | `conda create -n qtpy-env python=3.11 pyside6 -y`                |
| 复制daily-env为daily-env-copy | `conda create -n daily-env-copy --clone daily-env -y`          |
| 更新daily-env的Python到3.11.9 | `conda install -n daily-env python=3.11.9 -y`                  |
| 删除test_env环境     | `conda env remove -n test_env -y`                                    |

## 三、包管理（安装/更新/卸载/查看）
| 功能                 | 指令                                                                 |
|----------------------|----------------------------------------------------------------------|
| 查看当前环境所有包   | `conda list`                                                         |
| 查看daily-env的numpy版本 | `conda list -n daily-env numpy`                                   |
| 搜索numpy可用版本    | `conda search numpy`                                                 |
| 在qtpy-env安装PySide6 | `conda install -n qtpy-env pyside6 -y`                              |
| 在daily_dev安装numpy1.26 | `conda install -n daily_dev numpy=1.26 -y`                        |
| 安装多个包（当前环境） | `conda install pandas matplotlib -y`                                |
| 更新当前环境numpy    | `conda update numpy -y`                                              |
| 更新mkdocs-env的所有包 | `conda update -n mkdocs-env --all -y`                              |
| 更新conda本身        | `conda update conda -y`                                              |
| 卸载daily-env的pandas | `conda remove -n daily-env pandas -y`                               |
| 清理未使用包缓存     | `conda clean -p -y`                                                  |
| 清理所有缓存（释放空间） | `conda clean -y --all`                                             |

## 四、镜像源配置（加速下载）
| 功能                 | 指令                                                                 |
|----------------------|----------------------------------------------------------------------|
| 添加清华镜像源       | `conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/` |
| 添加清华main源       | `conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/` |
| 添加conda-forge源    | `conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/` |
| 显示下载源           | `conda config --set show_channel_urls yes`                           |
| 查看当前镜像源       | `conda config --show-sources`                                        |
| 重置为默认镜像源     | `conda config --remove-key channels`                                 |

## 五、项目专属（环境导出/导入/一键搭建）
| 功能                 | 指令                                                                 |
|----------------------|----------------------------------------------------------------------|
| 导出当前环境到yml    | `conda env export > environment.yml`                                 |
| 导入yml文件重建环境  | `conda env create -f environment.yml -y`                             |
| 一键搭建qtpy-env环境 | `conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/; conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/; conda config --set show_channel_urls yes; conda create -n qtpy-env python=3.11 -y; conda activate qtpy-env; conda install pyside6 numpy=1.26 -y` |
| 运行qtpy项目（示例路径） | `cd E:\Documents\VSCode_project; python main.py`                    |

## 六、问题排查（修复环境/解决识别问题）
| 功能                 | 指令                                                                 |
|----------------------|----------------------------------------------------------------------|
| 检查conda路径是否存在 | `Test-Path "C:\Users\coolzest\miniconda3\Scripts\conda.exe"`          |
| 修复损坏的test_env    | `conda clean --all -y; conda env remove -n test_env -y; conda create -n test_env python=3.11 -y` |
| 解决conda激活失败    | `conda init powershell; restart-shell`（重启终端生效）               |

## 七、快捷组合指令（高效操作）
| 功能                 | 指令                                                                 |
|----------------------|----------------------------------------------------------------------|
| 快速激活qtpy-env+更新所有包 | `conda activate qtpy-env && conda update --all -y`                 |
| 备份daily-env+清理缓存 | `conda activate daily-env && conda env export > daily-env.yml && conda clean -y --all` |
| 一键清理所有缓存+查看环境 | `conda clean -y --all && conda env list`                             |