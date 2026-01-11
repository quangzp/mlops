# 📚 Hướng Dẫn Chạy Documentation

Dự án sử dụng **MkDocs** với **Material Theme** để tạo documentation website.

---

## 🚀 Cách Chạy Documentation

### Bước 1: Cài Đặt Dependencies

```bash
# Cài đặt MkDocs và dependencies
pip install -r requirements-dev.txt

# Hoặc cài riêng
pip install mkdocs==1.5.3 mkdocs-material==9.5.3 mkdocstrings[python]==0.24.0
```

### Bước 2: Chạy Documentation Server (Development Mode)

```bash
# Cách 1: Dùng Makefile (khuyến nghị)
make docs

# Cách 2: Dùng mkdocs trực tiếp
mkdocs serve
```

**Kết quả:**
- Documentation sẽ chạy tại: **http://127.0.0.1:8000**
- Tự động reload khi bạn sửa file markdown trong `docs/`
- Nhấn `Ctrl+C` để dừng server

### Bước 3: Build Static Site (Production)

```bash
# Cách 1: Dùng Makefile
make docs-build

# Cách 2: Dùng mkdocs trực tiếp
mkdocs build
```

**Kết quả:**
- Build static site vào thư mục `site/`
- Có thể deploy lên GitHub Pages, Netlify, hoặc server tĩnh

---

## 📁 Cấu Trúc Documentation

```
docs/
├── index.md              # Trang chủ
├── getting_started.md    # Hướng dẫn bắt đầu
├── project_structure.md  # Cấu trúc dự án
├── configuration.md      # Cấu hình
├── training.md          # Training
├── api_reference.md     # API Reference
└── ...                  # Các file khác

mkdocs.yml               # Cấu hình MkDocs (ở root)
```

---

## 🔧 Các Lệnh MkDocs Hữu Ích

### Serve Documentation (Development)
```bash
mkdocs serve
# Hoặc với custom port
mkdocs serve --dev-addr=127.0.0.1:8080
```

### Build Static Site
```bash
mkdocs build
# Output: site/
```

### Build với Custom Directory
```bash
mkdocs build --site-dir=build/
```

### Validate Configuration
```bash
mkdocs build --strict  # Fail nếu có lỗi
```

### Preview Theme
```bash
mkdocs serve --theme=readthedocs  # Test theme khác
```

---

## 🎨 Customization

File cấu hình: `mkdocs.yml`

Có thể tùy chỉnh:
- Theme colors
- Navigation structure
- Plugins
- Markdown extensions
- Social links

---

## 📝 Thêm/Sửa Documentation

1. **Sửa file markdown trong `docs/`:**
   ```bash
   # Ví dụ: Sửa docs/getting_started.md
   nano docs/getting_started.md
   ```

2. **Cập nhật navigation trong `mkdocs.yml`:**
   ```yaml
   nav:
     - Home: index.md
     - Getting Started: getting_started.md
     - New Page: new_page.md  # Thêm trang mới
   ```

3. **MkDocs sẽ tự động reload** (nếu đang chạy `mkdocs serve`)

---

## 🌐 Deploy Documentation

### GitHub Pages
```bash
# Install plugin
pip install mkdocs-material[imaging]

# Deploy
mkdocs gh-deploy
```

### Netlify
1. Build command: `mkdocs build`
2. Publish directory: `site/`

### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /docs
RUN pip install mkdocs mkdocs-material
COPY . .
CMD ["mkdocs", "serve", "--dev-addr=0.0.0.0:8000"]
```

---

## ⚠️ Lưu Ý

1. **File rỗng**: Một số file trong `docs/` đang rỗng (0 bytes):
   - `index.md`
   - `getting_started.md`
   - `changelog.md`
   - `checkpointing.md`
   - etc.

   → Cần viết nội dung cho các file này

2. **Dependencies**: Đảm bảo đã cài `requirements-dev.txt` để có đầy đủ dependencies

3. **Port**: Nếu port 8000 bị chiếm, dùng `--dev-addr=127.0.0.1:8080`

---

## 🐛 Troubleshooting

### Lỗi: `mkdocs: command not found`
```bash
# Cài đặt lại
pip install mkdocs mkdocs-material
# Hoặc
pip install -r requirements-dev.txt
```

### Lỗi: File không tìm thấy trong nav
- Kiểm tra file có tồn tại trong `docs/`
- Kiểm tra tên file trong `mkdocs.yml` có đúng không

### Lỗi: Theme không load
```bash
# Cài lại theme
pip install --upgrade mkdocs-material
```

---

## 📚 Tài Liệu Tham Khảo

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [MkDocstrings](https://mkdocstrings.github.io/)
