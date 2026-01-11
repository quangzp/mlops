# Changelog

Tất cả các thay đổi đáng chú ý trong dự án này sẽ được ghi lại trong file này.

Format dựa trên [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
và dự án này tuân theo [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Hệ thống quản lý version tập trung với `mlops/__version__.py`
- Script `scripts/version.py` để quản lý và đồng bộ version
- Makefile commands cho version management (`make version`, `make version-sync`, `make version-bump`)

### Changed
- Đồng bộ version giữa `pyproject.toml`, `config.yaml`, và `api.py` thông qua version tập trung

## [0.1.0] - 2025-01-XX

### Added
- Cấu trúc dự án MLOps cơ bản
- DVC integration cho data versioning
- MLflow và Wandb integration cho experiment tracking
- FastAPI serving endpoint
- Documentation với MkDocs

### Changed
- Initial release

---

## Cách sử dụng Version Management

### Xem version hiện tại
```bash
make version
# hoặc
python3 scripts/version.py show
```

### Đồng bộ version giữa các file
```bash
make version-sync
# hoặc
python3 scripts/version.py sync
```

### Bump version
```bash
# Bump patch version (0.1.0 -> 0.1.1)
make version-bump PART=patch

# Bump minor version (0.1.0 -> 0.2.0)
make version-bump PART=minor

# Bump major version (0.1.0 -> 1.0.0)
make version-bump PART=major
```

### Semantic Versioning

- **MAJOR** version khi bạn thay đổi API không tương thích
- **MINOR** version khi bạn thêm chức năng mới nhưng vẫn tương thích ngược
- **PATCH** version khi bạn sửa lỗi và vẫn tương thích ngược
