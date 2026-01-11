# Testing & Linting (Dev Tools)

## Tổng quan

Dự án sử dụng nhiều công cụ hỗ trợ phát triển (dev tools) để đảm bảo chất lượng code, dễ bảo trì và phát hiện lỗi sớm. Các công cụ chính bao gồm: kiểm tra style/lint (ruff), kiểm tra type (mypy), kiểm thử tự động (pytest), và pre-commit hook.

---

## 1. Kiểm tra style và lint với Ruff

- **Ruff** là công cụ lint Python cực nhanh, thay thế cho flake8, isort, pycodestyle, v.v.
- Được cấu hình trong `pyproject.toml`:
  - Kiểm tra coding style, sắp xếp import, phát hiện lỗi phổ biến, cảnh báo code phức tạp.
  - Có thể tự động format code.

### Cách sử dụng:
```bash
ruff check .
ruff format .
```

---

## 2. Kiểm tra type với mypy

- **mypy** giúp phát hiện lỗi type (kiểu dữ liệu) tĩnh trước khi chạy code.
- Được cấu hình trong `pyproject.toml` và chạy tự động qua pre-commit.

### Cách sử dụng:
```bash
mypy .
```
- Nếu gặp lỗi với các thư viện động (như wandb), hãy dùng `# type: ignore[attr-defined]` ở dòng code đó.

---

## 3. Kiểm thử tự động với pytest

- **pytest** là framework kiểm thử phổ biến cho Python.
- Các test case được đặt trong thư mục `tests/`.
- Hỗ trợ kiểm thử đơn vị, kiểm thử tích hợp, đo coverage, mock, v.v.

### Cách sử dụng:
```bash
pytest
```

---

## 4. Pre-commit hook

- Dự án sử dụng pre-commit để tự động kiểm tra code trước khi commit lên git.
- Các hook bao gồm: ruff, ruff-format, mypy, trim trailing whitespace, check yaml, check toml, v.v.

### Cài đặt pre-commit:
```bash
pip install pre-commit
pre-commit install
```

### Chạy thủ công:
```bash
pre-commit run --all-files
```

---

## 5. Quản lý dependencies

- Các package chính được liệt kê trong `requirements.txt`.
- Các công cụ dev/test (ruff, mypy, pytest, ...) nên cài trong môi trường ảo (`.venv`).

---

## 6. Một số lưu ý

- Luôn chạy pre-commit trước khi push code để đảm bảo code sạch và không lỗi.
- Nếu gặp lỗi lint hoặc type, hãy sửa theo hướng dẫn của tool hoặc thêm `# type: ignore` đúng chỗ.
- Có thể mở rộng thêm các tool khác như black, coverage, hoặc CI/CD tùy nhu cầu.

---

## 7. Tham khảo

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/en/stable/)
- [pytest Documentation](https://docs.pytest.org/en/stable/)
- [pre-commit Documentation](https://pre-commit.com/)

---
