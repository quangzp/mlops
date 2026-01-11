# Scripts

Thư mục chứa các utility scripts cho dự án.

## version.py

Script quản lý version cho dự án MLOps.

### Usage

```bash
# Xem version hiện tại
python3 scripts/version.py show

# Đồng bộ version giữa tất cả các file
python3 scripts/version.py sync

# Bump version
python3 scripts/version.py bump patch   # 0.1.0 -> 0.1.1
python3 scripts/version.py bump minor   # 0.1.0 -> 0.2.0
python3 scripts/version.py bump major   # 0.1.0 -> 1.0.0
```

### Files được quản lý

Script này tự động đồng bộ version trong các file sau:
- `mlops/__version__.py` (source of truth)
- `pyproject.toml`
- `mlops/config/config.yaml`
- `mlops/serving/api.py`

### Makefile Commands

Bạn cũng có thể sử dụng Makefile commands:

```bash
make version              # Show version
make version-sync         # Sync version
make version-bump PART=patch  # Bump version
```
