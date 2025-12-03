# 发布流程

## 1. 修改版本号

编辑 `pyproject.toml`：

```toml
version = "x.x.x"
```

版本号规则：
- `0.0.x` - 小修复/补丁
- `0.x.0` - 新功能
- `x.0.0` - 重大更新/破坏性变更

## 2. 构建

```bash
uv build
```

输出文件在 `dist/` 目录。

## 3. 发布到 PyPI

```bash
uv publish --token <YOUR_PYPI_TOKEN>
```

## 4. 验证

```bash
pip install --upgrade acetool
```

## 注意事项

- PyPI 不允许覆盖已发布版本，必须升级版本号
- 发布前确保所有代码修改已完成
- Token 保存在安全位置，不要提交到 Git
