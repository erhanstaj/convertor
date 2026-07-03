# 1. En hafif Python sürümünü kullanıldı
FROM python:3.12-slim

# 2. Çalışma klasörümüzü /app olarak belirledik
WORKDIR /app

# 3. İhtiyacımız olan kodları ve kuralları konteynerin içine kopyaladık
COPY core/ /app/core/
COPY helpers/ /app/helpers/
COPY interfaces/ /app/interfaces/
COPY main.py /app/main.py
COPY company_rules.json /app/company_rules.json

# 4. Sunucunun dışarıdan bağlayacağı klasörler için boş yerler açtık
RUN mkdir -p /app/test_jsonlar /app/eski_sistemler /app/sonuclar

# 5. Konteyner çalıştığında arayüzsüz (headless) motoru tetikliyoruz
ENTRYPOINT ["python", "main.py"]
CMD ["--html"]
