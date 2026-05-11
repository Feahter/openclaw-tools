# commit skill

智能生成 git commit message，支持 Conventional Commits 格式。

## 使用方式

```
@feather commit [选项]
```

## 选项

- `--dry-run` — 仅显示 commit message，不执行 commit
- `--type <type>` — 指定类型（feat/fix/docs/style/refactor/test/chore）
- `-m <msg>` — 直接指定 commit message

## 示例

```
@feather commit                    # AI 生成 commit message
@feather commit --dry-run         # 预览 message
@feather commit --type fix        # 指定类型
```

## 输出格式

支持 Conventional Commits：
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```
